import secrets

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.services.email_service import EmailNotificationService

User = get_user_model()
OTP_EXPIRY_MINUTES = 10
OTP_EXPIRY_SECONDS = OTP_EXPIRY_MINUTES * 60
MAX_OTP_ATTEMPTS = 5


def _otp_cache_key(identifier: str) -> str:
    return f"password_reset_otp:{identifier.strip().lower()}"


def _find_user(identifier: str):
    cleaned = (identifier or "").strip()
    if not cleaned:
        return None

    # Match by email
    if "@" in cleaned:
        return (
            User.objects.filter(email__iexact=cleaned, is_active=True)
            .order_by("-created_at")
            .first()
        )

    # Match by 10-digit phone number (with or without +91)
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    return (
        User.objects.filter(
            Q(phone_number=cleaned)
            | Q(phone_number=digits)
            | Q(phone_number=f"+91{digits}"),
            is_active=True,
        )
        .order_by("-created_at")
        .first()
    )


# ==========================================================
# 1. SEND FORGOT PASSWORD OTP TO EMAIL
# Accepts email OR phone_number in "email" field
# ==========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_send_otp(request):
    identifier = (
        request.data.get("email")
        or request.data.get("phone_number")
        or ""
    ).strip()

    if not identifier:
        return Response(
            {
                "success": False,
                "message": "Email or phone number is required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = _find_user(identifier)
    if not user:
        return Response(
            {
                "success": False,
                "message": "No active account found with that email or phone number.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if not user.email:
        return Response(
            {
                "success": False,
                "message": "This account does not have an email address linked.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp_code = f"{secrets.randbelow(900000) + 100000}"

    try:
        EmailNotificationService.send_forgot_password_otp(
            email=user.email,
            otp=otp_code,
            first_name=getattr(user, "first_name", "") or "",
        )
    except Exception as exc:
        return Response(
            {
                "success": False,
                "message": f"Failed to send email OTP: {str(exc)}",
                "data": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "phone_number": getattr(user, "phone_number", ""),
        "otp": otp_code,
        "is_verified": False,
        "attempts": 0,
    }

    cache.set(_otp_cache_key(identifier), payload, timeout=OTP_EXPIRY_SECONDS)
    cache.set(_otp_cache_key(user.email), payload, timeout=OTP_EXPIRY_SECONDS)

    print(
        f"📩 Forgot Password OTP sent -> phone={user.phone_number}, email={user.email}"
    )

    return Response(
        {
            "success": True,
            "message": f"A 6-digit reset code has been sent to {user.email}.",
            "data": {
                "email": user.email,
                "phone_number": getattr(user, "phone_number", ""),
                "expires_in_minutes": OTP_EXPIRY_MINUTES,
            },
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# 2. VERIFY FORGOT PASSWORD OTP
# ==========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_verify_otp(request):
    identifier = (
        request.data.get("email")
        or request.data.get("phone_number")
        or ""
    ).strip()
    otp = (request.data.get("otp") or "").strip()

    if not identifier or not otp:
        return Response(
            {
                "success": False,
                "message": "Email/phone and OTP are required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    key = _otp_cache_key(identifier)
    record = cache.get(key)

    if not record:
        return Response(
            {
                "success": False,
                "message": "OTP expired or not found. Please request a new code.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if record["attempts"] >= MAX_OTP_ATTEMPTS:
        cache.delete(key)
        return Response(
            {
                "success": False,
                "message": "Too many failed attempts. Please request a new code.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if record["otp"] != otp:
        record["attempts"] += 1
        cache.set(key, record, timeout=OTP_EXPIRY_SECONDS)
        return Response(
            {"success": False, "message": "Invalid OTP code.", "data": None},
            status=status.HTTP_400_BAD_REQUEST,
        )

    record["is_verified"] = True
    cache.set(key, record, timeout=OTP_EXPIRY_SECONDS)

    return Response(
        {
            "success": True,
            "message": "OTP verified successfully. You can now set a new password.",
            "data": {
                "email": record["email"],
                "phone_number": record.get("phone_number", ""),
                "verified": True,
            },
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# 3. RESET PASSWORD WITH VERIFIED OTP
# ==========================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_reset(request):
    identifier = (
        request.data.get("email")
        or request.data.get("phone_number")
        or ""
    ).strip()
    otp = (request.data.get("otp") or "").strip()
    new_password = request.data.get("new_password") or ""
    confirm_password = request.data.get("confirm_password") or ""

    if not identifier or not otp or not new_password:
        return Response(
            {
                "success": False,
                "message": "Email/phone, OTP, and new_password are required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(new_password) < 6:
        return Response(
            {
                "success": False,
                "message": "Password must be at least 6 characters long.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if confirm_password and new_password != confirm_password:
        return Response(
            {"success": False, "message": "Passwords do not match.", "data": None},
            status=status.HTTP_400_BAD_REQUEST,
        )

    key = _otp_cache_key(identifier)
    record = cache.get(key)

    if not record or record["otp"] != otp:
        return Response(
            {
                "success": False,
                "message": "Invalid or expired OTP. Please request a new code.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(id=record["user_id"], is_active=True).first()
    if not user:
        return Response(
            {"success": False, "message": "User account not found.", "data": None},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])

    cache.delete(key)
    cache.delete(_otp_cache_key(user.email))

    print(
        f"✅ Password updated for phone={user.phone_number}, email={user.email}, role={user.role}"
    )

    EmailNotificationService.send_password_changed_email(
        email=user.email,
        first_name=getattr(user, "first_name", "") or "",
    )

    return Response(
        {
            "success": True,
            "message": f"Password updated for {user.phone_number}. Please log in with your new password.",
            "data": {
                "phone_number": user.phone_number,
                "email": user.email,
            },
        },
        status=status.HTTP_200_OK,
    )