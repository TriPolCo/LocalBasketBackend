from django.db import transaction

from apps.accounts.models.user import User
from apps.accounts.services.customer_service import CustomerService


class AuthService:

    @staticmethod
    @transaction.atomic
    def register_customer(
        phone_number,
        password,
        first_name=None,
        last_name=None,
        email=None,
    ):
        # Create authentication user
        user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=User.Role.CUSTOMER,
        )

        # Create customer profile
        customer = CustomerService.create_customer(
            user=user
        )

        return user, customer

    @staticmethod
    def login_user(phone_number, password):

        user = User.objects.filter(
            phone_number=phone_number
        ).first()

        if not user:
            raise ValueError(
                "Invalid phone number or password."
            )

        if not user.check_password(password):
            raise ValueError(
                "Invalid phone number or password."
            )

        if not user.is_active:
            raise ValueError(
                "Your account is inactive."
            )

        return user

    @staticmethod
    @transaction.atomic
    def update_profile_image(
        user,
        profile_image_url,
        profile_image_public_id,
    ):
        if not profile_image_url:
            raise ValueError(
                "Profile image URL is required."
            )

        if not profile_image_public_id:
            raise ValueError(
                "Profile image public ID is required."
            )

        # Store old public ID.
        # This can be used later to delete the old
        # image from Cloudinary.
        old_public_id = user.profile_image_public_id

        user.profile_image_url = profile_image_url
        user.profile_image_public_id = profile_image_public_id

        user.save(
            update_fields=[
                "profile_image_url",
                "profile_image_public_id",
            ]
        )

        return {
            "user": user,
            "old_public_id": old_public_id,
        }

    @staticmethod
    def get_current_user(user):
        """
        Return the currently authenticated user.
        """
        return User.objects.filter(
            id=user.id,
            is_active=True,
        ).first()