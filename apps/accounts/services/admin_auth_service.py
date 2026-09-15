from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models.user import User


def admin_login(phone_number, password):

    user = authenticate(
        phone_number=phone_number,
        password=password,
    )

    if not user:
        raise AuthenticationFailed(
            "Invalid phone number or password."
        )

    if not user.is_active:
        raise AuthenticationFailed(
            "Your account is inactive."
        )

    if user.role != User.Role.ADMIN:
        raise AuthenticationFailed(
            "You are not authorized as an admin."
        )

    if not user.is_staff:
        raise AuthenticationFailed(
            "Admin access is not enabled for this account."
        )

    refresh = RefreshToken.for_user(user)

    return {
        "user": user,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }