from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.products.services.flash_sale_service import (
    FlashSaleService
)

from apps.products.serializers.flash_sale_serializer import (
    FlashSaleProductSerializer
)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_flash_sale_products(request):

    variants = FlashSaleService.get_flash_sale_products()

    serializer = FlashSaleProductSerializer(
        variants,
        many=True
    )

    return Response(
        {
            "success": True,
            "message": "Flash sale products fetched successfully.",
            "count": len(serializer.data),
            "data": serializer.data,
        },
        status=status.HTTP_200_OK
    )