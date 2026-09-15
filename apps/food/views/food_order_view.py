from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.food.serializers.food_order_serializer import (
    FoodOrderPlaceSerializer,
    FoodOrderSerializer,
)

from apps.food.services.food_order_service import (
    FoodOrderService,
)


def get_customer(request):
    return request.user.customer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_food_order(request):

    serializer = FoodOrderPlaceSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = get_customer(request)

    order = FoodOrderService.place_order(
        customer=customer,
        address_id=serializer.validated_data["address_id"],
        payment_method=serializer.validated_data[
            "payment_method"
        ],
        customer_note=serializer.validated_data.get(
            "customer_note"
        ),
    )

    response_serializer = FoodOrderSerializer(order)

    return Response(
        {
            "success": True,
            "message": "Food order placed successfully.",
            "data": response_serializer.data,
        },
        status=201,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_food_orders(request):

    customer = get_customer(request)

    orders = FoodOrderService.get_orders(
        customer
    )

    serializer = FoodOrderSerializer(
        orders,
        many=True,
    )

    return Response({
        "success": True,
        "message": "Food orders fetched successfully.",
        "data": serializer.data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_food_order(request, order_id):

    customer = get_customer(request)

    order = FoodOrderService.get_order(
        customer=customer,
        order_id=order_id,
    )

    serializer = FoodOrderSerializer(order)

    return Response({
        "success": True,
        "message": "Food order fetched successfully.",
        "data": serializer.data,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancel_food_order(request, order_id):

    customer = get_customer(request)

    order = FoodOrderService.cancel_order(
        customer=customer,
        order_id=order_id,
    )

    serializer = FoodOrderSerializer(order)

    return Response({
        "success": True,
        "message": "Food order cancelled successfully.",
        "data": serializer.data,
    })