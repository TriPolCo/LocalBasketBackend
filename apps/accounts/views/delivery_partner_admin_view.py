from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.models.user import User

from apps.accounts.serializers.delivery_partner_serializer import (
    DeliveryPartnerCreateSerializer,
    DeliveryPartnerUpdateSerializer,
    DeliveryPartnerSerializer,
)

from apps.accounts.services.delivery_partner_service import (
    DeliveryPartnerService,
)


class IsAdmin(IsAuthenticated):

    def has_permission(
        self,
        request,
        view,
    ):

        return (
            super().has_permission(
                request,
                view,
            )
            and request.user.role == User.Role.ADMIN
            and request.user.is_staff
        )


@api_view(["POST"])
@permission_classes([IsAdmin])
def create_delivery_partner(request):

    serializer = DeliveryPartnerCreateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    delivery_partner = (
        DeliveryPartnerService
        .create_delivery_partner(
            serializer.validated_data
        )
    )

    response_serializer = (
        DeliveryPartnerSerializer(
            delivery_partner
        )
    )

    return Response(
        {
            "success": True,
            "message": (
                "Delivery partner created successfully."
            ),
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_delivery_partners(request):

    delivery_partners = (
        DeliveryPartnerService
        .get_delivery_partners()
    )

    serializer = DeliveryPartnerSerializer(
        delivery_partners,
        many=True,
    )

    return Response({
        "success": True,
        "message": (
            "Delivery partners fetched successfully."
        ),
        "data": serializer.data,
    })


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_delivery_partner(
    request,
    delivery_partner_id,
):

    delivery_partner = (
        DeliveryPartnerService
        .get_delivery_partner(
            delivery_partner_id
        )
    )

    serializer = DeliveryPartnerSerializer(
        delivery_partner
    )

    return Response({
        "success": True,
        "message": (
            "Delivery partner fetched successfully."
        ),
        "data": serializer.data,
    })


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_delivery_partner(
    request,
    delivery_partner_id,
):

    serializer = DeliveryPartnerUpdateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    delivery_partner = (
        DeliveryPartnerService
        .update_delivery_partner(
            delivery_partner_id,
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
            "Delivery partner updated successfully."
        ),
        "data": response_serializer.data,
    })


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_delivery_partner(
    request,
    delivery_partner_id,
):

    DeliveryPartnerService.delete_delivery_partner(
        delivery_partner_id
    )

    return Response({
        "success": True,
        "message": (
            "Delivery partner deleted successfully."
        ),
        "data": None,
    })