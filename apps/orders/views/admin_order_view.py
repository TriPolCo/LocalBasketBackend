from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin

from apps.orders.serializers.admin_order_serializer import (
    AdminOrderSerializer,
)
from apps.orders.services.admin_order_service import (
    AdminOrderService,
)
from apps.orders.serializers.order_status_serializer import AdminOrderStatusUpdateSerializer
from apps.orders.services.order_service import OrderService
from apps.orders.models.order import Order



@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_all_orders(request):

    orders = AdminOrderService.get_all_orders()

    serializer = AdminOrderSerializer(
        orders,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "All orders fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def admin_update_order_status(request, order_id):

    if request.user.role != "ADMIN":
        return Response(
            {
                "success": False,
                "message": "Only admin can update order status.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Order not found.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AdminOrderStatusUpdateSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "message": "Invalid order status.",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_status = serializer.validated_data["status"]
    try:
        order = OrderService.update_order_status(
            order,
            new_status,
        )
    except Exception as exc:
        return Response(
            {
                "success": False,
                "message": str(exc),
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "success": True,
            "message": "Order status updated successfully.",
            "data": {
                "id": str(order.id),
                "order_number": order.order_number,
                "old_status": order.status if False else None,
                "status": order.status,
                "payment_status": order.payment_status,
                "delivered_at": order.delivered_at,
                "cancelled_at": order.cancelled_at,
                "updated_at": order.updated_at,
            },
        },
        status=status.HTTP_200_OK,
    )