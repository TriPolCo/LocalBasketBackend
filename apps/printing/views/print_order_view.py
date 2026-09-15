from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.printing.serializers.print_order_serializer import (
    CreatePrintOrderSerializer,
    PrintOrderSerializer,
)

from apps.printing.services.print_order_service import (
    PrintOrderService,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_print_order(request):

    serializer = CreatePrintOrderSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = request.user.customer_profile

    order = PrintOrderService.create_print_order(
        customer=customer,
        **serializer.validated_data,
    )

    response_serializer = PrintOrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Print order created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_print_orders(request):

    customer = request.user.customer_profile

    orders = PrintOrderService.get_customer_orders(
        customer=customer
    )

    serializer = PrintOrderSerializer(
        orders,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Print orders fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_print_order(request, order_id):

    customer = request.user.customer_profile

    order = PrintOrderService.get_customer_order(
        customer=customer,
        order_id=order_id,
    )

    serializer = PrintOrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Print order fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancel_print_order(request, order_id):

    customer = request.user.customer_profile

    order = PrintOrderService.cancel_order(
        customer=customer,
        order_id=order_id,
    )

    serializer = PrintOrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Print order cancelled successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )