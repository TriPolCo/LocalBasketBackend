import random
import re
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models.customer import Customer
from apps.accounts.serializers.auth_serializer import (
    CustomerRegisterSerializer,
    UserLoginSerializer,
)
from apps.accounts.services.auth_service import AuthService
from apps.accounts.services.otp_service import OTPService
from apps.accounts.services.email_service import EmailNotificationService

User = get_user_model()
DEFAULT_CALL_TO_ORDER_PHONE = "+919337172633"


# ========================================================
# 1. SEND PHONE OTP (SMS)
# ========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    phone_number = request.data.get("phone_number")

    if not phone_number:
        return Response(
            {
                "success": False,
                "message": "Phone number is required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = OTPService.send_otp(phone_number)

    if result.get("success"):
        return Response(
            {
                "success": True,
                "message": result.get("message", "OTP sent successfully."),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "success": False,
            "message": result.get("message", "Failed to send OTP."),
            "data": None,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


# ========================================================
# 2. VERIFY PHONE OTP & LOGIN / SIGNUP
# ========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    phone_number = request.data.get("phone_number")
    otp = request.data.get("otp")

    if not phone_number:
        return Response(
            {
                "success": False,
                "message": "Phone number is required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not otp:
        return Response(
            {
                "success": False,
                "message": "OTP is required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    is_valid = OTPService.verify_otp(phone_number, otp)

    if not is_valid:
        return Response(
            {
                "success": False,
                "message": "Invalid or expired OTP. Please try again.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    clean_phone = OTPService.clean_phone_number(phone_number)

    # 1. Find existing user or create a new Customer
    user, created = User.objects.get_or_create(
        phone_number=clean_phone,
        defaults={
            "is_active": True,
            "role": User.Role.CUSTOMER,
            "phone_verified": True,
        },
    )

    # 2. Automatically mark phone_verified = True in database
    if not user.phone_verified:
        user.phone_verified = True
        user.save(update_fields=["phone_verified"])

    # 3. Ensure Customer profile exists (prevents 'User has no customer_profile')
    customer, _ = Customer.objects.get_or_create(user=user)
    if not customer.is_verified:
        customer.is_verified = True
        customer.save(update_fields=["is_verified"])

    # 4. Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "success": True,
            "message": "Phone number verified successfully. Login successful.",
            "data": {
                "is_new_user": created,
                "user": {
                    "id": str(user.id),
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "email_verified": user.email_verified,
                    "phone_verified": user.phone_verified,
                    "store_phone_number": getattr(user, "store_phone_number", None),
                },
                "customer": {
                    "id": str(customer.id),
                    "is_verified": customer.is_verified,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
        },
        status=status.HTTP_200_OK,
    )


# ========================================================
# 3. SIGNUP: SEND EMAIL VERIFICATION OTP
# ========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def send_signup_email_otp(request):
    raw_email = request.data.get("email", "").strip()

    if not raw_email:
        return Response(
            {"success": False, "message": "Email address is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate email format
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, raw_email):
        return Response(
            {"success": False, "message": "Please enter a valid email address."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    clean_email = raw_email.lower()

    # Reject if an account with this email already exists
    if User.objects.filter(email__iexact=clean_email).exists():
        return Response(
            {
                "success": False,
                "message": "An account with this email address already exists. Please log in.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Save to Django cache for 10 minutes (600s)
    cache.set(f"signup_email_otp_{clean_email}", otp, timeout=600)

    # Send email via Gmail SMTP
    try:
        EmailNotificationService.send_signup_verification_otp(clean_email, otp)
        print(f"📧 [SIGNUP OTP] Verification code {otp} sent to {clean_email}")
    except Exception as exc:
        print(f"❌ Failed to send signup email OTP: {exc}")
        return Response(
            {
                "success": False,
                "message": "Failed to send verification email. Please check your address or try again.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "success": True,
            "message": f"Verification code sent to {clean_email}.",
        },
        status=status.HTTP_200_OK,
    )


# ========================================================
# 4. SIGNUP: VERIFY EMAIL OTP
# ========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_signup_email_otp(request):
    raw_email = request.data.get("email", "").strip()
    entered_otp = str(request.data.get("otp", "")).strip()

    if not raw_email or not entered_otp:
        return Response(
            {"success": False, "message": "Email and OTP code are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    clean_email = raw_email.lower()
    cached_otp = cache.get(f"signup_email_otp_{clean_email}")

    if not cached_otp or str(cached_otp) != entered_otp:
        return Response(
            {"success": False, "message": "Invalid or expired verification code."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Clean up OTP and mark email verified in cache for 30 minutes
    cache.delete(f"signup_email_otp_{clean_email}")
    cache.set(f"signup_email_verified_{clean_email}", True, timeout=1800)

    return Response(
        {
            "success": True,
            "message": "Email verified successfully.",
            "data": {"email": clean_email, "verified": True},
        },
        status=status.HTTP_200_OK,
    )


# ========================================================
# 5. REGISTER (STRICT BACKEND EMAIL VERIFICATION CHECK)
# ========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = CustomerRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data.get("email")
    if not email:
        return Response(
            {"success": False, "message": "Email address is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    clean_email = email.strip().lower()

    # 🔒 STRICT BACKEND CHECK: Verify email was validated via OTP!
    if not cache.get(f"signup_email_verified_{clean_email}"):
        return Response(
            {
                "success": False,
                "message": "Please verify your email address via OTP before signing up.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user, customer = AuthService.register_customer(
        **serializer.validated_data
    )

    # Mark user email as verified
    if not user.email_verified:
        user.email_verified = True
        user.save(update_fields=["email_verified"])

    # Clear verified token from cache
    cache.delete(f"signup_email_verified_{clean_email}")

    return Response(
        {
            "success": True,
            "message": "Customer registered successfully.",
            "data": {
                "user": {
                    "id": str(user.id),
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "email_verified": user.email_verified,
                    "phone_verified": user.phone_verified,
                },
                "customer": {
                    "id": str(customer.id),
                    "is_verified": customer.is_verified,
                },
            },
        },
        status=status.HTTP_201_CREATED,
    )


# ========================================================
# 6. LOGIN (PASSWORD-BASED)
# ========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = AuthService.login_user(**serializer.validated_data)
    except ValueError as error:
        return Response(
            {
                "success": False,
                "message": str(error),
                "data": None,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "success": True,
            "message": "Login successful.",
            "data": {
                "user": {
                    "id": str(user.id),
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "email_verified": user.email_verified,
                    "phone_verified": user.phone_verified,
                    "store_phone_number": getattr(user, "store_phone_number", None),
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
        },
        status=status.HTTP_200_OK,
    )


# ========================================================
# 7. 💾 STORE / CALL TO ORDER PHONE (DATABASE-BACKED)
# ========================================================
@api_view(["GET", "PATCH", "POST"])
@permission_classes([AllowAny])
def store_call_to_order_phone(request):
    # ========================================================
    # A. PUBLIC GET: Read directly from MySQL Database
    # ========================================================
    if request.method == "GET":
        admin_user = (
            User.objects.filter(role=User.Role.ADMIN, is_active=True)
            .exclude(store_phone_number__isnull=True)
            .exclude(store_phone_number="")
            .order_by("-updated_at")
            .first()
        )

        phone_number = (
            admin_user.store_phone_number
            if (admin_user and admin_user.store_phone_number)
            else DEFAULT_CALL_TO_ORDER_PHONE
        )

        return Response(
            {
                "success": True,
                "message": "Store phone number fetched successfully.",
                "data": {
                    "store_phone_number": phone_number,
                    "phone_number": phone_number,
                },
            },
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # B. ADMIN PATCH/POST: Save directly to MySQL Database!
    # ========================================================
    if request.method in ["PATCH", "POST"]:
        if not request.user.is_authenticated or (
            getattr(request.user, "role", None) != User.Role.ADMIN and not request.user.is_staff
        ):
            return Response(
                {
                    "success": False,
                    "message": "Permission denied. Only admins can update the store phone number.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        new_phone = str(
            request.data.get("store_phone_number")
            or request.data.get("phone_number")
            or ""
        ).strip()

        clean_digits = re.sub(r"[^\d]", "", new_phone)
        if len(clean_digits) < 10:
            return Response(
                {
                    "success": False,
                    "message": "Please enter a valid phone number (at least 10 digits).",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 💾 Save to MySQL database column users.store_phone_number
        request.user.store_phone_number = new_phone
        request.user.save(update_fields=["store_phone_number", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Store phone number updated successfully in the database.",
                "data": {
                    "store_phone_number": new_phone,
                    "phone_number": new_phone,
                },
            },
            status=status.HTTP_200_OK,
        )


# ========================================================
# 8. UPDATE PROFILE IMAGE
# ========================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile_image(request):
    profile_image_url = request.data.get("profile_image_url")
    profile_image_public_id = request.data.get("profile_image_public_id")

    if not profile_image_url:
        return Response(
            {"success": False, "message": "Profile image URL is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not profile_image_public_id:
        return Response(
            {"success": False, "message": "Profile image public ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = AuthService.update_profile_image(
            user=request.user,
            profile_image_url=profile_image_url,
            profile_image_public_id=profile_image_public_id,
        )
        user = result["user"]

        return Response(
            {
                "success": True,
                "message": "Profile image updated successfully.",
                "data": {
                    "profile_image_url": user.profile_image_url,
                    "profile_image_public_id": user.profile_image_public_id,
                },
            },
            status=status.HTTP_200_OK,
        )
    except ValueError as e:
        return Response(
            {"success": False, "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ========================================================
# 9. GET CURRENT USER
# ========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = AuthService.get_current_user(request.user)

    if not user:
        return Response(
            {"success": False, "message": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "success": True,
            "message": "User information fetched successfully.",
            "data": {
                "id": str(user.id),
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
                "profile_image_url": user.profile_image_url,
                "profile_image_public_id": user.profile_image_public_id,
                "store_phone_number": getattr(user, "store_phone_number", None),
                "is_active": user.is_active,
            },
        },
        status=status.HTTP_200_OK,
    )