from rest_framework import serializers

from apps.accounts.models.user import User
from apps.accounts.models.delivery_partner import DeliveryPartner


class DeliveryPartnerCreateSerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=15
    )

    password = serializers.CharField(
        min_length=8,
        write_only=True
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    first_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    gender = serializers.ChoiceField(
        choices=DeliveryPartner.Gender.choices,
        required=False,
        allow_null=True,
    )

    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
    )

    profile_image_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    profile_image_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    is_active = serializers.BooleanField(
        required=False,
        default=True,
    )

    def validate_phone_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Phone number is required."
            )

        if User.objects.filter(
            phone_number=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )

        return value

    def validate_email(self, value):
        if value:
            value = value.strip().lower()

            if User.objects.filter(
                email__iexact=value
            ).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )

        return value


class DeliveryPartnerUpdateSerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=15,
        required=False,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    first_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    gender = serializers.ChoiceField(
        choices=DeliveryPartner.Gender.choices,
        required=False,
        allow_null=True,
    )

    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
    )

    profile_image_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    profile_image_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    is_active = serializers.BooleanField(
        required=False,
    )


class DeliveryPartnerSerializer(serializers.ModelSerializer):

    user_id = serializers.UUIDField(
        source="user.id",
        read_only=True,
    )

    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )

    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )

    profile_image_url = serializers.URLField(
        source="user.profile_image_url",
        read_only=True,
    )

    profile_image_public_id = serializers.CharField(
        source="user.profile_image_public_id",
        read_only=True,
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True,
    )

    is_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True,
    )

    class Meta:
        model = DeliveryPartner

        fields = [
            "id",
            "user_id",

            "phone_number",
            "email",
            "first_name",
            "last_name",

            "profile_image_url",
            "profile_image_public_id",

            "role",
            "is_active",

            "gender",
            "date_of_birth",

            "is_available",

            "average_rating",
            "total_deliveries",
            "completed_deliveries",
            "cancelled_deliveries",

            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


class DeliveryPartnerLoginSerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=15
    )

    password = serializers.CharField(
        write_only=True
    )


class DeliveryPartnerChangePasswordSerializer(
    serializers.Serializer
):

    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        min_length=8,
        write_only=True
    )

    def validate(self, attrs):

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": (
                    "New password must be different "
                    "from the old password."
                )
            })

        return attrs


class DeliveryPartnerAvailabilitySerializer(
    serializers.Serializer
):

    is_available = serializers.BooleanField()