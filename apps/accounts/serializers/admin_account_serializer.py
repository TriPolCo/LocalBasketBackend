from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class SuperUserUpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs["current_password"]
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        # Verify current password
        if not user.check_password(current_password):
            raise serializers.ValidationError({
                "current_password":
                    "Current password is incorrect."
            })

        # New password confirmation
        if new_password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password":
                    "New passwords do not match."
            })

        # Prevent same password
        if user.check_password(new_password):
            raise serializers.ValidationError({
                "new_password":
                    "New password must be different from the current password."
            })

        # Django password validation
        from django.contrib.auth.password_validation import (
            validate_password,
        )

        validate_password(
            new_password,
            user=user,
        )

        return attrs


class SuperUserUpdateEmailSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    new_email = serializers.EmailField(
        required=True,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs["current_password"]
        new_email = attrs["new_email"].lower().strip()

        # Verify current password
        if not user.check_password(current_password):
            raise serializers.ValidationError({
                "current_password":
                    "Current password is incorrect."
            })

        # Check whether email is already used
        if User.objects.filter(
            email__iexact=new_email
        ).exclude(
            id=user.id
        ).exists():
            raise serializers.ValidationError({
                "new_email":
                    "This email is already registered."
            })

        # Prevent unnecessary update
        if (
            user.email
            and user.email.lower() == new_email
        ):
            raise serializers.ValidationError({
                "new_email":
                    "This is already your current email."
            })

        attrs["new_email"] = new_email

        return attrs


class SuperUserUpdatePhoneSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    new_phone_number = serializers.CharField(
        required=True,
        max_length=15,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs["current_password"]

        new_phone_number = (
            attrs["new_phone_number"]
            .strip()
        )

        # Verify current password
        if not user.check_password(current_password):
            raise serializers.ValidationError({
                "current_password":
                    "Current password is incorrect."
            })

        # Check duplicate phone
        if User.objects.filter(
            phone_number=new_phone_number
        ).exclude(
            id=user.id
        ).exists():
            raise serializers.ValidationError({
                "new_phone_number":
                    "This phone number is already registered."
            })

        # Prevent unnecessary update
        if (
            user.phone_number
            and user.phone_number == new_phone_number
        ):
            raise serializers.ValidationError({
                "new_phone_number":
                    "This is already your current phone number."
            })

        attrs["new_phone_number"] = new_phone_number

        return attrs


class SuperUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile_image_url",
            "phone_verified",
            "email_verified",
        ]
        read_only_fields = fields