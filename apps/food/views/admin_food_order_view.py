from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response

from rest_framework import status

from apps.food.services.admin_food_order_service import (
    AdminFoodOrderService,
)

from apps.food.serializers.admin_food_order_serializer import (
    AdminFoodOrderSerializer,
    UpdateFoodDeliveryFeeSerializer,
)


# ==========================================================
# ADMIN CHECK
# ==========================================================

def is_admin(request):

    return (
        request.user.is_authenticated
        and request.user.role == "ADMIN"
        and request.user.is_staff
    )


# ==========================================================
# GET ALL FOOD ORDERS
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_get_food_orders(request):

    if not is_admin(request):

        return Response(
            {
                "success": False,
                "message":
                    "You are not authorized to access food orders.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    status_value = request.query_params.get(
        "status"
    )

    search = request.query_params.get(
        "search"
    )

    # ------------------------------------------------------
    # GET ORDERS
    # ------------------------------------------------------

    orders = (
        AdminFoodOrderService
        .get_orders(
            status_value=status_value,
            search=search,
        )
    )

    # ------------------------------------------------------
    # SERIALIZE
    # ------------------------------------------------------

    serializer = AdminFoodOrderSerializer(
        orders,
        many=True,
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    return Response(
        {
            "success": True,
            "message":
                "Food orders fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# GET FOOD ORDER DETAIL
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_get_food_order(
    request,
    order_id,
):

    if not is_admin(request):

        return Response(
            {
                "success": False,
                "message":
                    "You are not authorized to access this order.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------
    # GET ORDER
    # ------------------------------------------------------

    order = (
        AdminFoodOrderService
        .get_order(
            order_id=order_id
        )
    )

    # ------------------------------------------------------
    # SERIALIZE
    # ------------------------------------------------------

    serializer = AdminFoodOrderSerializer(
        order
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    return Response(
        {
            "success": True,
            "message":
                "Food order details fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# UPDATE FOOD ORDER STATUS
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def admin_update_food_order_status(
    request,
    order_id,
):

    if not is_admin(request):

        return Response(
            {
                "success": False,
                "message":
                    "You are not authorized to update this order.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------
    # GET STATUS
    # ------------------------------------------------------

    new_status = request.data.get(
        "status"
    )

    if not new_status:

        return Response(
            {
                "success": False,
                "message":
                    "status is required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # UPDATE STATUS
    # ------------------------------------------------------

    order = (
        AdminFoodOrderService
        .update_status(
            order_id=order_id,
            new_status=new_status,
        )
    )

    # ------------------------------------------------------
    # SERIALIZE
    # ------------------------------------------------------

    serializer = AdminFoodOrderSerializer(
        order
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    return Response(
        {
            "success": True,
            "message":
                "Food order status updated successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# UPDATE FOOD ORDER DELIVERY FEE
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def admin_update_food_delivery_fee(
    request,
    order_id,
):

    if not is_admin(request):

        return Response(
            {
                "success": False,
                "message":
                    "You are not authorized to update delivery fee.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------
    # VALIDATE REQUEST
    # ------------------------------------------------------

    serializer = UpdateFoodDeliveryFeeSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    # ------------------------------------------------------
    # UPDATE DELIVERY FEE
    # ------------------------------------------------------

    order = (
        AdminFoodOrderService
        .update_delivery_fee(
            order_id=order_id,
            delivery_fee=(
                serializer
                .validated_data["delivery_fee"]
            ),
        )
    )

    # ------------------------------------------------------
    # SERIALIZE UPDATED ORDER
    # ------------------------------------------------------

    response_serializer = (
        AdminFoodOrderSerializer(
            order
        )
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    return Response(
        {
            "success": True,
            "message":
                "Food delivery fee updated successfully.",
            "data":
                response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# ASSIGN DELIVERY PARTNER
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_assign_food_delivery(
    request,
    order_id,
):

    if not is_admin(request):

        return Response(
            {
                "success": False,
                "message":
                    "You are not authorized to assign delivery partner.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------
    # GET DELIVERY PARTNER ID
    # ------------------------------------------------------

    delivery_partner_id = request.data.get(
        "delivery_partner_id"
    )

    if not delivery_partner_id:

        return Response(
            {
                "success": False,
                "message":
                    "delivery_partner_id is required.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # ASSIGN DELIVERY PARTNER
    # ------------------------------------------------------

    AdminFoodOrderService.assign_delivery_partner(
        order_id=order_id,
        delivery_partner_id=delivery_partner_id,
    )

    # ------------------------------------------------------
    # GET UPDATED ORDER
    # ------------------------------------------------------

    order = (
        AdminFoodOrderService
        .get_order(
            order_id=order_id
        )
    )

    # ------------------------------------------------------
    # SERIALIZE
    # ------------------------------------------------------

    serializer = AdminFoodOrderSerializer(
        order
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    return Response(
        {
            "success": True,
            "message":
                "Delivery partner assigned successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )