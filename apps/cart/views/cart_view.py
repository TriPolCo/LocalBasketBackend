from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.cart.serializers.cart_serializer import (
    AddToCartSerializer,
    CartSerializer,
    UpdateCartQuantitySerializer,
)

from apps.cart.services.cart_service import CartService


# ==========================================================
# GET CART
# ==========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):

    customer = request.user.customer_profile

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Cart fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# ADD TO CART
# ==========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):

    serializer = AddToCartSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = request.user.customer_profile

    CartService.add_to_cart(
        customer=customer,
        **serializer.validated_data,
    )

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Product added to cart successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# UPDATE QUANTITY
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_cart_quantity(
    request,
    item_id,
):

    serializer = UpdateCartQuantitySerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = request.user.customer_profile

    CartService.update_quantity(
        customer=customer,
        item_id=item_id,
        quantity=serializer.validated_data["quantity"],
    )

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Cart quantity updated successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# INCREASE QUANTITY
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def increase_cart_quantity(
    request,
    item_id,
):

    customer = request.user.customer_profile

    CartService.increase_quantity(
        customer=customer,
        item_id=item_id,
    )

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Cart quantity increased successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# DECREASE QUANTITY
# ==========================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def decrease_cart_quantity(
    request,
    item_id,
):

    customer = request.user.customer_profile

    CartService.decrease_quantity(
        customer=customer,
        item_id=item_id,
    )

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Cart quantity decreased successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# REMOVE ITEM
# ==========================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_cart_item(
    request,
    item_id,
):

    customer = request.user.customer_profile

    CartService.remove_item(
        customer=customer,
        item_id=item_id,
    )

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Product removed from cart successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# CLEAR CART
# ==========================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_cart(request):

    customer = request.user.customer_profile

    CartService.clear_cart(
        customer=customer
    )

    cart = CartService.get_cart(
        customer=customer
    )

    serializer = CartSerializer(cart)

    return Response(
        {
            "success": True,
            "message": "Cart cleared successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )