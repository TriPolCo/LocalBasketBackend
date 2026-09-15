from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.products.serializers.variant_value_serializer import (
    VariantValueCreateSerializer,
    VariantValueResponseSerializer,
)
from apps.products.services.variant_value_service import (
    VariantValueService,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_variant_value(request):

    serializer = VariantValueCreateSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    variant_value = VariantValueService.create_value(
        **serializer.validated_data
    )

    response_serializer = VariantValueResponseSerializer(
        variant_value
    )

    return Response(
        {
            "success": True,
            "message": "Variant value created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )