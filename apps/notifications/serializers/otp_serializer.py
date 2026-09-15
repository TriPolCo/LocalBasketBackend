from rest_framework import serializers

from apps.notifications.models.otp import EmailOTP


class SendEmailOTPSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default=EmailOTP.PURPOSE_SIGNUP,
    )

    def validate_email(self, value):

        return value.strip().lower()


class VerifyEmailOTPSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default=EmailOTP.PURPOSE_SIGNUP,
    )

    def validate_email(self, value):

        return value.strip().lower()

    def validate_otp(self, value):

        value = value.strip()

        if not value.isdigit():

            raise serializers.ValidationError(
                "OTP must contain only numbers."
            )

        if len(value) != 6:

            raise serializers.ValidationError(
                "OTP must be 6 digits."
            )

        return value