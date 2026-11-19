from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin

from apps.orders.models.order import Order
from apps.orders.serializers.admin_order_detail_serializer import (
    AdminOrderDetailSerializer,
)
from apps.orders.serializers.admin_order_serializer import (
    AdminOrderSerializer,
    AdminSaveExpressBillSerializer,
    AdminUpdateDeliveryFeeSerializer,
)
from apps.orders.serializers.order_serializer import OrderSerializer
from apps.orders.serializers.order_status_serializer import (
    AdminOrderStatusUpdateSerializer,
)
from apps.orders.services.admin_order_service import AdminOrderService
from apps.orders.services.order_service import OrderService


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


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_order_details(request, order_id):

    order = AdminOrderService.get_order_details(order_id)
    print("ORDER RESULT:", order)

    if not order:
        return Response(
            {
                "success": False,
                "message": "Order not found.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AdminOrderDetailSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Order details fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def admin_update_delivery_fee(
    request,
    order_id,
):

    serializer = AdminUpdateDeliveryFeeSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    order = AdminOrderService.update_delivery_fee(
        order_id=order_id,
        delivery_fee=serializer.validated_data[
            "delivery_fee"
        ],
    )

    response_serializer = OrderSerializer(
        order
    )

    return Response({
        "success": True,
        "message": "Delivery fee updated successfully.",
        "data": response_serializer.data,
    })


@api_view(["PATCH", "POST"])
@permission_classes([IsAdmin])
def admin_save_express_bill(request, order_id):

    serializer = AdminSaveExpressBillSerializer(
        data=request.data
    )
    serializer.is_valid(raise_exception=True)

    items_data = serializer.validated_data["items"]
    discount = serializer.validated_data.get(
        "discount",
        Decimal("0.00"),
    )
    delivery_fee = serializer.validated_data.get(
        "delivery_fee",
        None,
    )

    try:
        with transaction.atomic():
            order = (
                Order.objects
                .select_for_update()
                .get(id=order_id)
            )

            cleaned_items = [
                {
                    "quantity_label": item["quantity_label"].strip(),
                    "product_name": item["product_name"].strip(),
                    "price": float(item["price"]),
                }
                for item in items_data
            ]

            subtotal = sum(
                (Decimal(str(item["price"])) for item in items_data),
                Decimal("0.00"),
            )

            if delivery_fee is not None:
                order.delivery_fee = delivery_fee

            order.manual_items = cleaned_items
            order.subtotal = subtotal
            order.discount = discount
            order.total_amount = max(
                Decimal("0.00"),
                subtotal + order.delivery_fee - discount + order.tax,
            )

            update_fields = [
                "manual_items",
                "subtotal",
                "discount",
                "delivery_fee",
                "total_amount",
                "updated_at",
            ]

            if order.status == Order.Status.PENDING_REVIEW:
                order.status = Order.Status.PROCESSING
                update_fields.append("status")

            order.save(update_fields=update_fields)

        return Response(
            {
                "success": True,
                "message": "Express order bill saved successfully.",
                "data": AdminOrderDetailSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )

    except Order.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Order not found.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )