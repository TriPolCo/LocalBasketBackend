from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.accounts.serializers.delivery_partner_serializer import (
    DeliveryPartnerLoginSerializer,
    DeliveryPartnerSerializer,
    DeliveryPartnerChangePasswordSerializer,
    DeliveryPartnerAvailabilitySerializer,
    DeliveryPartnerUpdateSerializer,
)

from apps.accounts.services.delivery_partner_auth_service import (
    DeliveryPartnerAuthService,
)

from apps.accounts.services.delivery_partner_service import (
    DeliveryPartnerService,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def delivery_partner_login(request):

    serializer = DeliveryPartnerLoginSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    result = (
        DeliveryPartnerAuthService
        .login(
            phone_number=serializer.validated_data[
                "phone_number"
            ],
            password=serializer.validated_data[
                "password"
            ],
        )
    )

    delivery_partner = result[
        "delivery_partner"
    ]

    user_serializer = DeliveryPartnerSerializer(
        delivery_partner
    )

    return Response({
        "success": True,
        "message": (
            "Delivery partner login successful."
        ),
        "data": {
            "user": user_serializer.data,
            "access": result["access"],
            "refresh": result["refresh"],
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_partner_profile(
    request
):

    delivery_partner = (
        DeliveryPartnerAuthService
        .get_profile(
            request.user
        )
    )

    serializer = DeliveryPartnerSerializer(
        delivery_partner
    )

    return Response({
        "success": True,
        "message": (
            "Delivery partner profile fetched successfully."
        ),
        "data": serializer.data,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_delivery_partner_profile(
    request
):

    serializer = DeliveryPartnerUpdateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    delivery_partner = (
        DeliveryPartnerAuthService
        .update_profile(
            request.user,
            serializer.validated_data,
        )
    )

    response_serializer = (
        DeliveryPartnerSerializer(
            delivery_partner
        )
    )

    return Response({
        "success": True,
        "message": (
            "Profile updated successfully."
        ),
        "data": response_serializer.data,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_delivery_partner_password(
    request
):

    serializer = (
        DeliveryPartnerChangePasswordSerializer(
            data=request.data
        )
    )

    serializer.is_valid(
        raise_exception=True
    )

    DeliveryPartnerAuthService.change_password(
        user=request.user,
        old_password=serializer.validated_data[
            "old_password"
        ],
        new_password=serializer.validated_data[
            "new_password"
        ],
    )

    return Response({
        "success": True,
        "message": (
            "Password changed successfully."
        ),
        "data": None,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_delivery_partner_availability(
    request
):

    serializer = (
        DeliveryPartnerAvailabilitySerializer(
            data=request.data
        )
    )

    serializer.is_valid(
        raise_exception=True
    )

    delivery_partner = (
        DeliveryPartnerAuthService
        .get_profile(
            request.user
        )
    )

    delivery_partner = (
        DeliveryPartnerService
        .update_availability(
            delivery_partner=delivery_partner,
            is_available=serializer.validated_data[
                "is_available"
            ],
        )
    )

    response_serializer = (
        DeliveryPartnerSerializer(
            delivery_partner
        )
    )

    return Response({
        "success": True,
        "message": (
            "Availability updated successfully."
        ),
        "data": response_serializer.data,
    })