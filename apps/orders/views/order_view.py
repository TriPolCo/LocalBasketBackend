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
from apps.notifications.pusher_service import trigger_admin_order_notification


# ========================================================
# 1. PLACE REGULAR CART ORDER
# ========================================================
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

    # Real-time WebSocket trigger to React Admin
    try:
        trigger_admin_order_notification(response_serializer.data)
    except Exception as e:
        print(f"Failed to send real-time notification: {e}")

    return Response(
        {
            "success": True,
            "message": "Order placed successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ========================================================
# 2. PLACE UPLOAD PAPER LIST ORDER (STRING IMAGE URL)
# ========================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_list_order(request):

    address_id = request.data.get("address_id")
    image_url = request.data.get("image_url")
    instructions = request.data.get("instructions", "") or request.data.get("notes", "")

    if not address_id:
        return Response(
            {
                "success": False,
                "message": "address_id is required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not image_url or not str(image_url).strip():
        return Response(
            {
                "success": False,
                "message": "image_url string is required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    customer = request.user.customer_profile

    order = OrderService.place_upload_list_order(
        customer=customer,
        address_id=address_id,
        image_url=str(image_url).strip(),
        instructions=instructions,
    )

    response_serializer = OrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Paper list order placed successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ========================================================
# 3. PLACE TYPED WRITTEN LIST ORDER
# ========================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def type_list_order(request):

    address_id = request.data.get("address_id")
    items_raw = request.data.get("items_raw")
    instructions = request.data.get("instructions", "")

    if not address_id:
        return Response(
            {
                "success": False,
                "message": "address_id is required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not items_raw or not str(items_raw).strip():
        return Response(
            {
                "success": False,
                "message": "items_raw is required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    customer = request.user.customer_profile

    order = OrderService.place_type_list_order(
        customer=customer,
        address_id=address_id,
        items_raw=str(items_raw).strip(),
        instructions=instructions,
    )

    response_serializer = OrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Written list order placed successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ========================================================
# 4. GET CUSTOMER ORDERS
# ========================================================
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


# ========================================================
# 5. GET SINGLE ORDER DETAIL
# ========================================================
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


# ========================================================
# 6. CANCEL ORDER
# ========================================================
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