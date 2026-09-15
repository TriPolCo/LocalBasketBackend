from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.products.serializers.variant_attribute_serializer import (
    VariantAttributeCreateSerializer,
    VariantAttributeResponseSerializer,
)
from apps.products.services.variant_attribute_service import (
    VariantAttributeService,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_variant_attribute(request):

    serializer = VariantAttributeCreateSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    attribute = VariantAttributeService.create_attribute(
        **serializer.validated_data
    )

    response_serializer = VariantAttributeResponseSerializer(
        attribute
    )

    return Response(
        {
            "success": True,
            "message": "Variant attribute created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_variant_attributes(request):

    include_inactive = (
        request.query_params.get("include_inactive", "false").lower()
        == "true"
    )

    attributes = VariantAttributeService.get_attributes(
        include_inactive=include_inactive
    )

    serializer = VariantAttributeResponseSerializer(
        attributes,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Variant attributes fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )