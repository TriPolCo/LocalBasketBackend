from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.brands.serializers.brand_serializer import (
    BrandCreateSerializer,
    BrandResponseSerializer,
)
from apps.brands.services.brand_service import BrandService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_brand(request):

    serializer = BrandCreateSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    brand = BrandService.create_brand(
        **serializer.validated_data
    )

    response_serializer = BrandResponseSerializer(
        brand
    )

    return Response(
        {
            "success": True,
            "message": "Brand created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )