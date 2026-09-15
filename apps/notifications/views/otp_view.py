from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.notifications.serializers.otp_serializer import (
    SendEmailOTPSerializer,
    VerifyEmailOTPSerializer,
)

from apps.notifications.services.otp_service import (
    OTPService,
)


# ============================================================
# SEND EMAIL OTP
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def send_email_otp(request):

    serializer = SendEmailOTPSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    OTPService.send_otp(
        **serializer.validated_data
    )

    return Response(
        {
            "success": True,
            "message": "OTP sent successfully to your email.",
            "data": None,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# VERIFY EMAIL OTP
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email_otp(request):

    serializer = VerifyEmailOTPSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    OTPService.verify_otp(
        **serializer.validated_data
    )

    return Response(
        {
            "success": True,
            "message": "OTP verified successfully.",
            "data": {
                "email": serializer.validated_data["email"],
                "verified": True,
            },
        },
        status=status.HTTP_200_OK,
    )