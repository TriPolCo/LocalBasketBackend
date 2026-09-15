from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models.user import User
from apps.accounts.models.delivery_partner import DeliveryPartner


class DeliveryPartnerService:

    @staticmethod
    @transaction.atomic
    def create_delivery_partner(data):

        phone_number = data["phone_number"]

        if User.objects.filter(
            phone_number=phone_number
        ).exists():
            raise ValidationError({
                "phone_number": (
                    "A user with this phone number "
                    "already exists."
                )
            })

        email = data.get("email")

        if email and User.objects.filter(
            email__iexact=email
        ).exists():
            raise ValidationError({
                "email": (
                    "A user with this email "
                    "already exists."
                )
            })

        user = User.objects.create_user(
            phone_number=phone_number,
            password=data["password"],
            email=email,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            role=User.Role.DELIVERY_PARTNER,
            is_active=data.get(
                "is_active",
                True,
            ),
        )

        user.profile_image_url = data.get(
            "profile_image_url"
        )

        user.profile_image_public_id = data.get(
            "profile_image_public_id"
        )

        user.save(
            update_fields=[
                "profile_image_url",
                "profile_image_public_id",
            ]
        )

        delivery_partner = DeliveryPartner.objects.create(
            user=user,
            gender=data.get("gender"),
            date_of_birth=data.get(
                "date_of_birth"
            ),
        )

        return delivery_partner

    @staticmethod
    def get_delivery_partners():

        return (
            DeliveryPartner.objects
            .select_related("user")
            .order_by("-created_at")
        )

    @staticmethod
    def get_delivery_partner(
        delivery_partner_id
    ):

        try:
            return (
                DeliveryPartner.objects
                .select_related("user")
                .get(
                    id=delivery_partner_id
                )
            )

        except DeliveryPartner.DoesNotExist:
            raise ValidationError({
                "delivery_partner": (
                    "Delivery partner not found."
                )
            })

    @staticmethod
    @transaction.atomic
    def update_delivery_partner(
        delivery_partner_id,
        data,
    ):

        delivery_partner = (
            DeliveryPartner.objects
            .select_for_update()
            .select_related("user")
            .get(id=delivery_partner_id)
        )

        user = delivery_partner.user

        if "phone_number" in data:

            phone_number = data["phone_number"]

            if User.objects.filter(
                phone_number=phone_number
            ).exclude(
                id=user.id
            ).exists():

                raise ValidationError({
                    "phone_number": (
                        "A user with this phone number "
                        "already exists."
                    )
                })

            user.phone_number = phone_number

        if "email" in data:

            email = data["email"]

            if email and User.objects.filter(
                email__iexact=email
            ).exclude(
                id=user.id
            ).exists():

                raise ValidationError({
                    "email": (
                        "A user with this email "
                        "already exists."
                    )
                })

            user.email = email

        user_fields = [
            "first_name",
            "last_name",
            "profile_image_url",
            "profile_image_public_id",
            "is_active",
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

    @staticmethod
    @transaction.atomic
    def delete_delivery_partner(
        delivery_partner_id
    ):

        try:
            delivery_partner = (
                DeliveryPartner.objects
                .select_related("user")
                .get(
                    id=delivery_partner_id
                )
            )

        except DeliveryPartner.DoesNotExist:
            raise ValidationError({
                "delivery_partner": (
                    "Delivery partner not found."
                )
            })

        user = delivery_partner.user

        user.delete()

        return True

    @staticmethod
    @transaction.atomic
    def update_availability(
        delivery_partner,
        is_available,
    ):

        delivery_partner.is_available = is_available

        delivery_partner.save(
            update_fields=[
                "is_available",
                "updated_at",
            ]
        )

        return delivery_partner