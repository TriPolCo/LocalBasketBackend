from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.food.serializers.food_cart_serializer import (
    AddFoodToCartSerializer,
    UpdateFoodCartItemSerializer,
    FoodCartSerializer,
)

from apps.food.services.food_cart_service import (
    FoodCartService,
)


def get_customer(request):
    return request.user.customer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_food_cart(request):

    customer = get_customer(request)

    cart = FoodCartService.get_cart(customer)

    serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food cart fetched successfully.",
        "data": serializer.data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_food_to_cart(request):

    serializer = AddFoodToCartSerializer(
        data=request.data
    )
    serializer.is_valid(raise_exception=True)

    customer = get_customer(request)

    cart = FoodCartService.add_item(
        customer=customer,
        food_item_id=serializer.validated_data["food_item_id"],
        variant_id=serializer.validated_data["variant_id"],
        quantity=serializer.validated_data["quantity"],
        addons=serializer.validated_data.get("addons", []),
    )

    response_serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food item added to cart successfully.",
        "data": response_serializer.data,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_food_cart_item(request, item_id):

    serializer = UpdateFoodCartItemSerializer(
        data=request.data
    )
    serializer.is_valid(raise_exception=True)

    customer = get_customer(request)

    cart = FoodCartService.update_item(
        customer=customer,
        item_id=item_id,
        quantity=serializer.validated_data.get("quantity"),
        addons=serializer.validated_data.get("addons"),
    )

    response_serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food cart item updated successfully.",
        "data": response_serializer.data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def increase_food_cart_item(request, item_id):

    customer = get_customer(request)

    cart = FoodCartService.increase_item(
        customer,
        item_id,
    )

    serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food quantity increased successfully.",
        "data": serializer.data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decrease_food_cart_item(request, item_id):

    customer = get_customer(request)

    cart = FoodCartService.decrease_item(
        customer,
        item_id,
    )

    serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food quantity decreased successfully.",
        "data": serializer.data,
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_food_cart_item(request, item_id):

    customer = get_customer(request)

    cart = FoodCartService.remove_item(
        customer,
        item_id,
    )

    serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food item removed from cart successfully.",
        "data": serializer.data,
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_food_cart(request):

    customer = get_customer(request)

    cart = FoodCartService.clear_cart(customer)

    serializer = FoodCartSerializer(cart)

    return Response({
        "success": True,
        "message": "Food cart cleared successfully.",
        "data": serializer.data,
    })