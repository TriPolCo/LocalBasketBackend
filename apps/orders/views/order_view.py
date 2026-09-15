from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.serializers.order_serializer import (
    PlaceOrderSerializer,
    OrderSerializer,
)
from apps.orders.services.order_service import OrderService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_order(request):

    serializer = PlaceOrderSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = request.user.customer_profile

    order = OrderService.place_order(
        customer=customer,
        **serializer.validated_data,
    )

    response_serializer = OrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Order placed successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders(request):

    customer = request.user.customer_profile

    orders = OrderService.get_orders(
        customer=customer
    )

    serializer = OrderSerializer(
        orders,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Orders fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):

    customer = request.user.customer_profile

    order = OrderService.get_order(
        customer=customer,
        order_id=order_id,
    )

    serializer = OrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Order fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):

    customer = request.user.customer_profile

    order = OrderService.cancel_order(
        customer=customer,
        order_id=order_id,
    )

    serializer = OrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Order cancelled successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )