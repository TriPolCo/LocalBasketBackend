from django.contrib.auth import authenticate

from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models.user import User
from apps.accounts.models.delivery_partner import (
    DeliveryPartner,
)


class DeliveryPartnerAuthService:

    @staticmethod
    def login(
        phone_number,
        password,
    ):

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

        if user.role != User.Role.DELIVERY_PARTNER:

            raise AuthenticationFailed(
                "You are not authorized as a delivery partner."
            )

        try:
            delivery_partner = (
                DeliveryPartner.objects
                .select_related("user")
                .get(user=user)
            )

        except DeliveryPartner.DoesNotExist:

            raise AuthenticationFailed(
                "Delivery partner profile not found."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "delivery_partner": delivery_partner,
            "access": str(
                refresh.access_token
            ),
            "refresh": str(refresh),
        }

    @staticmethod
    def change_password(
        user,
        old_password,
        new_password,
    ):

        if not user.check_password(
            old_password
        ):

            raise AuthenticationFailed(
                "Current password is incorrect."
            )

        user.set_password(
            new_password
        )

        user.save(
            update_fields=[
                "password",
                "updated_at",
            ]
        )

        return True

    @staticmethod
    def get_profile(user):

        try:
            return (
                DeliveryPartner.objects
                .select_related("user")
                .get(user=user)
            )

        except DeliveryPartner.DoesNotExist:

            raise AuthenticationFailed(
                "Delivery partner profile not found."
            )

    @staticmethod
    def update_profile(
        user,
        data,
    ):

        delivery_partner = (
            DeliveryPartnerAuthService
            .get_profile(user)
        )

        user_fields = [
            "first_name",
            "last_name",
            "email",
            "profile_image_url",
            "profile_image_public_id",
        ]

        for field in user_fields:

            if field in data:
                setattr(
                    user,
                    field,
                    data[field],
                )

        user.save()

        partner_fields = [
            "gender",
            "date_of_birth",
        ]

        for field in partner_fields:

            if field in data:
                setattr(
                    delivery_partner,
                    field,
                    data[field],
                )

        delivery_partner.save()

        return delivery_partner