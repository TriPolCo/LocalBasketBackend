from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.products.serializers.product import (
    ProductCreateSerializer,
    ProductCreateResponseSerializer,
ProductListSerializer
)



from apps.products.services.product_service import (
    ProductService,
)


# ============================================================
# CREATE PRODUCT
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product(request):

    serializer = ProductCreateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    product = ProductService.create_product(
        **serializer.validated_data
    )

    response_serializer = ProductCreateResponseSerializer(
        product
    )

    return Response(
        {
            "success": True,
            "message": "Product created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# GET PRODUCTS
# ============================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def get_products(request):
    category = request.query_params.get("category")

    products = ProductService.get_products(
        category=category,
    )

    serializer = ProductListSerializer(
        products,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Products fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
@permission_classes([AllowAny])
def get_product_by_id(request, product_id):
    product = ProductService.get_product_by_id(product_id)

    serializer = ProductListSerializer(product)

    return Response(
        {
            "success": True,
            "message": "Product fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )