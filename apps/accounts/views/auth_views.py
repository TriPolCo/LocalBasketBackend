from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers.auth_serializer import CustomerRegisterSerializer, UserLoginSerializer
from apps.accounts.services.auth_service import AuthService


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = CustomerRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user, customer = AuthService.register_customer(
        **serializer.validated_data
    )

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


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):

    serializer = UserLoginSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    try:
        user = AuthService.login_user(
            **serializer.validated_data
        )

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
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile_image(request):

    profile_image_url = request.data.get(
        "profile_image_url"
    )

    profile_image_public_id = request.data.get(
        "profile_image_public_id"
    )

    if not profile_image_url:
        return Response(
            {
                "success": False,
                "message": "Profile image URL is required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not profile_image_public_id:
        return Response(
            {
                "success": False,
                "message": "Profile image public ID is required.",
            },
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
                    "profile_image_public_id": (
                        user.profile_image_public_id
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )

    except ValueError as e:
        return Response(
            {
                "success": False,
                "message": str(e),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):

    user = AuthService.get_current_user(
        request.user
    )

    if not user:
        return Response(
            {
                "success": False,
                "message": "User not found.",
            },
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
                "profile_image_public_id": (
                    user.profile_image_public_id
                ),
                "is_active": user.is_active,
            },
        },
        status=status.HTTP_200_OK,
    )