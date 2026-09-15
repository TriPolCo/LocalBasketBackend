from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin

from apps.orders.serializers.admin_order_serializer import (
    AdminOrderSerializer,
)
from apps.orders.services.admin_order_service import (
    AdminOrderService,
)


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