from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.delivery.serializers import (
    DeliveryAssignmentCreateSerializer,
    DeliveryAssignmentSerializer,
)
from apps.delivery.serializers.delivery_assignment_serializer import (
    DeliveryProofSerializer,
)
from apps.delivery.services import DeliveryAssignmentService


def _get_logged_in_delivery_partner(user):
    partner = getattr(user, "delivery_partner_profile", None)
    if not partner:
        raise PermissionDenied("Only delivery partners can access this resource.")
    return partner


# ==========================================================
# ADMIN - ASSIGN ORDER
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_delivery_order(request):
    serializer = DeliveryAssignmentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    if validated_data.get("food_order_id"):
        assignment = DeliveryAssignmentService.assign_food_order(
            food_order_id=validated_data["food_order_id"],
            delivery_partner_id=validated_data["delivery_partner_id"],
        )
        message = "Food order assigned to delivery partner successfully."
    else:
        assignment = DeliveryAssignmentService.assign_order(
            order_id=validated_data["order_id"],
            delivery_partner_id=validated_data["delivery_partner_id"],
        )
        message = "Order assigned to delivery partner successfully."

    response_serializer = DeliveryAssignmentSerializer(assignment)
    return Response(
        {
            "success": True,
            "message": message,
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ==========================================================
# ADMIN - GET ALL ASSIGNMENTS
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_assignments(request):
    status_filter = request.query_params.get("status")
    assignments = DeliveryAssignmentService.get_assignments(
        status_filter=status_filter
    )
    serializer = DeliveryAssignmentSerializer(assignments, many=True)

    return Response(
        {
            "success": True,
            "message": "Delivery assignments fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DELIVERY PARTNER - GET MY ASSIGNMENTS
# Supports: ?status=active | ?status=history | ?status=ASSIGNED
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_delivery_assignments(request):
    delivery_partner = _get_logged_in_delivery_partner(request.user)
    scope = request.query_params.get("status")

    assignments = DeliveryAssignmentService.get_partner_assignments(
        delivery_partner=delivery_partner,
        scope=scope,
    )
    serializer = DeliveryAssignmentSerializer(assignments, many=True)

    return Response(
        {
            "success": True,
            "message": "Your delivery assignments fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DELIVERY PARTNER - SCAN QR / ORDER CODE
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def scan_delivery_assignment(request, code):
    delivery_partner = _get_logged_in_delivery_partner(request.user)

    assignment = DeliveryAssignmentService.find_partner_assignment_by_code(
        delivery_partner=delivery_partner,
        raw_code=code,
    )
    serializer = DeliveryAssignmentSerializer(assignment)

    return Response(
        {
            "success": True,
            "message": "Delivery assignment matched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# GET ASSIGNMENT DETAIL
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_assignment(request, assignment_id):
    assignment = DeliveryAssignmentService.get_assignment(assignment_id)
    serializer = DeliveryAssignmentSerializer(assignment)

    return Response(
        {
            "success": True,
            "message": "Delivery assignment fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DELIVERY PARTNER - ACCEPT ASSIGNMENT
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_delivery_assignment(request, assignment_id):
    delivery_partner = _get_logged_in_delivery_partner(request.user)

    assignment = DeliveryAssignmentService.accept_assignment(
        assignment_id=assignment_id,
        delivery_partner_id=delivery_partner.id,
    )
    serializer = DeliveryAssignmentSerializer(assignment)

    return Response(
        {
            "success": True,
            "message": "Delivery assignment accepted.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DELIVERY PARTNER - START DELIVERY (IN_TRANSIT)
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_delivery_assignment(request, assignment_id):
    delivery_partner = _get_logged_in_delivery_partner(request.user)

    assignment = DeliveryAssignmentService.start_delivery(
        assignment_id=assignment_id,
        delivery_partner_id=delivery_partner.id,
    )
    serializer = DeliveryAssignmentSerializer(assignment)

    return Response(
        {
            "success": True,
            "message": "Delivery started. Status is now In Transit.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DELIVERY PARTNER - COMPLETE DELIVERY (DELIVERED)
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_delivery_assignment(request, assignment_id):
    delivery_partner = _get_logged_in_delivery_partner(request.user)

    assignment = DeliveryAssignmentService.complete_delivery(
        assignment_id=assignment_id,
        delivery_partner_id=delivery_partner.id,
    )
    serializer = DeliveryAssignmentSerializer(assignment)

    return Response(
        {
            "success": True,
            "message": "Delivery marked as delivered.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DELIVERY PARTNER - UPLOAD DELIVERY PROOF
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_delivery_proof(request, assignment_id):
    serializer = DeliveryProofSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    delivery_partner = _get_logged_in_delivery_partner(request.user)

    assignment = DeliveryAssignmentService.upload_delivery_proof(
        assignment_id=assignment_id,
        delivery_partner_id=delivery_partner.id,
        delivery_image_url=validated_data["delivery_image_url"],
        delivery_image_public_id=validated_data["delivery_image_public_id"],
        payment_method=validated_data["payment_method"],
        payment_confirmed=validated_data.get("payment_confirmed", False),
    )

    response_serializer = DeliveryAssignmentSerializer(assignment)
    return Response(
        {
            "success": True,
            "message": "Delivery proof uploaded and order marked as delivered.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )