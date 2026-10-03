from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response
from rest_framework import status

from apps.delivery.serializers import (
    DeliveryAssignmentCreateSerializer,
    DeliveryAssignmentSerializer,
)

from apps.delivery.services import (
    DeliveryAssignmentService,
)

from apps.delivery.serializers.delivery_assignment_serializer import (
    DeliveryProofSerializer,
)


# ==========================================================
# ADMIN - ASSIGN ORDER
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_delivery_order(request):

    serializer = DeliveryAssignmentCreateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    validated_data = serializer.validated_data

    # ------------------------------------------------------
    # FOOD ORDER
    # ------------------------------------------------------

    if validated_data.get("food_order_id"):

        assignment = (
            DeliveryAssignmentService
            .assign_food_order(
                food_order_id=validated_data[
                    "food_order_id"
                ],
                delivery_partner_id=validated_data[
                    "delivery_partner_id"
                ],
            )
        )

        message = (
            "Food order assigned to "
            "delivery partner successfully."
        )

    # ------------------------------------------------------
    # NORMAL ORDER
    # ------------------------------------------------------

    else:

        assignment = (
            DeliveryAssignmentService
            .assign_order(
                order_id=validated_data[
                    "order_id"
                ],
                delivery_partner_id=validated_data[
                    "delivery_partner_id"
                ],
            )
        )

        message = (
            "Order assigned to "
            "delivery partner successfully."
        )

    response_serializer = (
        DeliveryAssignmentSerializer(
            assignment
        )
    )

    return Response(
        {
            "success": True,
            "message": message,
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ==========================================================
# GET ALL ASSIGNMENTS
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_assignments(request):

    assignments = (
        DeliveryAssignmentService
        .get_assignments()
    )

    serializer = DeliveryAssignmentSerializer(
        assignments,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": (
                "Delivery assignments "
                "fetched successfully."
            ),
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# GET ASSIGNMENT DETAIL
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_assignment(
    request,
    assignment_id,
):

    assignment = (
        DeliveryAssignmentService
        .get_assignment(
            assignment_id
        )
    )

    serializer = DeliveryAssignmentSerializer(
        assignment
    )

    return Response(
        {
            "success": True,
            "message": (
                "Delivery assignment "
                "fetched successfully."
            ),
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# UPLOAD DELIVERY PROOF
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_delivery_proof(
    request,
    assignment_id,
):

    serializer = DeliveryProofSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    # ------------------------------------------------------
    # Logged-in delivery partner
    # ------------------------------------------------------

    delivery_partner = (
        request.user
        .delivery_partner_profile
    )

    # ------------------------------------------------------
    # Upload proof
    # ------------------------------------------------------

    assignment = (
        DeliveryAssignmentService
        .upload_delivery_proof(
            assignment_id=assignment_id,
            delivery_partner=delivery_partner,
            data=serializer.validated_data,
        )
    )

    response_serializer = (
        DeliveryAssignmentSerializer(
            assignment
        )
    )

    return Response(
        {
            "success": True,
            "message": (
                "Delivery proof uploaded and "
                "order marked as delivered."
            ),
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# GET ALL ASSIGNMENTS
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_assignments(request):

    assignments = (
        DeliveryAssignmentService
        .get_assignments()
    )

    serializer = DeliveryAssignmentSerializer(
        assignments,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": (
                "Delivery assignments "
                "fetched successfully."
            ),
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )