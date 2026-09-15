from rest_framework import serializers

from apps.accounts.models.user import User


class CustomerRegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    first_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    def validate_phone_number(self, value):
        value = value.strip()

        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value



class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate_phone_number(self, value):
        return value.strip()