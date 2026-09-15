from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models.user import User


class SignupSerializer(serializers.Serializer):

    first_name = serializers.CharField(
        max_length=100,
        required=True,
    )

    last_name = serializers.CharField(
        max_length=100,
        required=True,
    )

    email = serializers.EmailField(
        required=True,
    )

    phone_number = serializers.CharField(
        max_length=15,
        required=True,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()

    def validate_phone_number(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be 10 digits."
            )

        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if User.objects.filter(
            phone_number=attrs["phone_number"]
        ).exists():
            raise serializers.ValidationError({
                "phone_number": "Phone number is already registered."
            })

        if User.objects.filter(
            email=attrs["email"]
        ).exists():
            raise serializers.ValidationError({
                "email": "Email is already registered."
            })

        return attrs