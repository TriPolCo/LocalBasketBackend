# apps/products/views/product_view.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.products.models.product import Product
from apps.products.serializers.product import (
    ProductCreateResponseSerializer,
    ProductCreateSerializer,
    ProductListSerializer,
)
from apps.products.services.product_service import ProductService


# ============================================================
# 1. CREATE PRODUCT
# ============================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product(request):
    serializer = ProductCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    product = ProductService.create_product(**serializer.validated_data)
    response_serializer = ProductCreateResponseSerializer(product)

    return Response(
        {
            "success": True,
            "message": "Product created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# 2. GET PRODUCTS
# ============================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def get_products(request):
    category = request.query_params.get("category")
    products = ProductService.get_products(category=category)

    serializer = ProductListSerializer(products, many=True)

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
def get_products_admin(request):
    category = request.query_params.get("category")
    products = ProductService.get_products_admin(category=category)

    serializer = ProductListSerializer(products, many=True)

    return Response(
        {
            "success": True,
            "message": "Products fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )



# ============================================================
# 3. GET PRODUCT BY ID
# ============================================================
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


# ============================================================
# 4. GET PRODUCTS BY CATEGORY
# ============================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def get_products_by_category(request, category_id):
    products = ProductService.get_products_by_category(category_id)
    serializer = ProductListSerializer(products, many=True)

    return Response(
        {
            "success": True,
            "message": "Products fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# 5. GET POPULAR PRODUCTS
# ============================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def get_popular_products(request):
    try:
        limit = int(request.query_params.get("limit", 10))
    except ValueError:
        limit = 10

    limit = max(1, min(limit, 50))
    products = ProductService.get_popular_products(limit=limit)

    serializer = ProductListSerializer(products, many=True)

    return Response(
        {
            "success": True,
            "message": "Popular products fetched successfully.",
            "count": len(serializer.data),
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# 6. TOGGLE / UPDATE PRODUCT STATUS (ACTIVE / INACTIVE)
# ============================================================
@api_view(["PATCH", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def toggle_product_status(request, product_id):
    """
    Toggle or explicitly set a Product's active/inactive status.
    - If 'is_active' is passed: sets it to that boolean.
    - If no payload or empty: directly flips the current status.
    """
    product = get_object_or_404(Product, id=product_id)

    # 1. Check if explicit status was passed in request body
    if "is_active" in request.data:
        val = request.data.get("is_active")
        if isinstance(val, str):
            product.is_active = val.lower() in ["true", "1", "yes"]
        else:
            product.is_active = bool(val)
    else:
        # Flip current status
        product.is_active = not product.is_active

    # 2. Save updated fields
    product.save(update_fields=["is_active", "updated_at"])

    status_label = "active" if product.is_active else "inactive"

    return Response(
        {
            "success": True,
            "message": f"Product '{product.name}' is now {status_label}.",
            "data": {
                "id": str(product.id),
                "name": product.name,
                "is_active": product.is_active,
                "updated_at": product.updated_at.isoformat(),
            },
        },
        status=status.HTTP_200_OK,
    )