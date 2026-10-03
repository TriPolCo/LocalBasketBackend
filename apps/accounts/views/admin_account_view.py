from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.serializers.admin_account_serializer import (
    SuperUserUpdatePasswordSerializer,
    SuperUserUpdateEmailSerializer,
    SuperUserUpdatePhoneSerializer, SuperUserProfileSerializer,
)


User = get_user_model()


def is_superuser(request):
    return (
        request.user.is_authenticated
        and request.user.is_superuser
    )


# ==========================================================
# UPDATE PASSWORD
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def superuser_update_password(request):

    if not is_superuser(request):
        return Response(
            {
                "success": False,
                "message":
                    "Only superusers can update this account.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = SuperUserUpdatePasswordSerializer(
        data=request.data,
        context={
            "request": request,
        },
    )

    serializer.is_valid(
        raise_exception=True
    )

    user = request.user

    user.set_password(
        serializer.validated_data["new_password"]
    )

    user.save(
        update_fields=[
            "password",
        ]
    )

    return Response(
        {
            "success": True,
            "message":
                "Password updated successfully.",
            "data": None,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# UPDATE EMAIL
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def superuser_update_email(request):

    if not is_superuser(request):
        return Response(
            {
                "success": False,
                "message":
                    "Only superusers can update this account.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = SuperUserUpdateEmailSerializer(
        data=request.data,
        context={
            "request": request,
        },
    )

    serializer.is_valid(
        raise_exception=True
    )

    user = request.user

    user.email = (
        serializer.validated_data["new_email"]
    )

    user.email_verified = False

    user.save(
        update_fields=[
            "email",
            "email_verified",
        ]
    )

    return Response(
        {
            "success": True,
            "message":
                "Email updated successfully.",
            "data": {
                "email": user.email,
                "email_verified": user.email_verified,
            },
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# UPDATE PHONE
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def superuser_update_phone(request):

    if not is_superuser(request):
        return Response(
            {
                "success": False,
                "message":
                    "Only superusers can update this account.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = SuperUserUpdatePhoneSerializer(
        data=request.data,
        context={
            "request": request,
        },
    )

    serializer.is_valid(
        raise_exception=True
    )

    user = request.user

    user.phone_number = (
        serializer.validated_data[
            "new_phone_number"
        ]
    )

    user.phone_verified = False

    user.save(
        update_fields=[
            "phone_number",
            "phone_verified",
        ]
    )

    return Response(
        {
            "success": True,
            "message":
                "Phone number updated successfully.",
            "data": {
                "phone_number": user.phone_number,
                "phone_verified": user.phone_verified,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_superuser_profile(request):

    if not is_superuser(request):
        return Response(
            {
                "success": False,
                "message":
                    "Only superusers can access this account.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = SuperUserProfileSerializer(
        request.user
    )

    return Response(
        {
            "success": True,
            "message":
                "Admin profile fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )