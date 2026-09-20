from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.categories.models.category import Category

from apps.categories.serializers.category_serializer import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    MainCategoryCreateSerializer,
    SubcategoryCreateSerializer,
    MainCategoryUpdateSerializer,
    SubcategoryUpdateSerializer,
)

from apps.categories.services.category_service import (
    get_main_categories,
    get_subcategories,
    get_category,
    create_main_category,
    create_subcategory,
    update_main_category,
    update_subcategory,
    delete_category,
    get_category_tree,
)


# ============================================================
# CATEGORY LIST
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def category_list(request):
    categories = get_main_categories()

    serializer = CategoryListSerializer(
        categories,
        many=True,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Categories fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )





@api_view(["GET"])
@permission_classes([AllowAny])
def category_list_public(request):
    categories = get_main_categories()

    serializer = CategoryListSerializer(
        categories,
        many=True,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Categories fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# CATEGORY TREE
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def category_tree(request):
    data = get_category_tree()

    return Response(
        {
            "message": "Category tree fetched successfully.",
            "data": data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# CREATE MAIN CATEGORY
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_category(request):
    serializer = MainCategoryCreateSerializer(
        data=request.data,
    )

    serializer.is_valid(
        raise_exception=True,
    )

    category = create_main_category(
        serializer.validated_data,
    )

    response_serializer = CategoryDetailSerializer(
        category,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Main category created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# CREATE SUBCATEGORY
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_subcategory_view(
    request,
    category_id,
):
    try:
        parent = Category.objects.get(
            id=category_id,
            parent__isnull=True,
        )

    except Category.DoesNotExist:
        return Response(
            {
                "message": "Main category not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = SubcategoryCreateSerializer(
        data=request.data,
        context={
            "parent": parent,
        },
    )

    serializer.is_valid(
        raise_exception=True,
    )

    subcategory = create_subcategory(
        parent=parent,
        validated_data=serializer.validated_data,
    )

    response_serializer = CategoryDetailSerializer(
        subcategory,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Subcategory created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# SUBCATEGORY LIST
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subcategory_list(
    request,
    category_id,
):
    subcategories = get_subcategories(
        category_id,
    )

    serializer = CategoryListSerializer(
        subcategories,
        many=True,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Subcategories fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# CATEGORY DETAIL
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def category_detail(
    request,
    category_id,
):
    category = get_category(
        category_id,
    )

    serializer = CategoryDetailSerializer(
        category,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Category fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# UPDATE MAIN CATEGORY
# ============================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_category(
    request,
    category_id,
):
    category = get_category(
        category_id,
    )

    if category.parent_id is not None:
        return Response(
            {
                "message": (
                    "This endpoint is only for main categories."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = MainCategoryUpdateSerializer(
        category,
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True,
    )

    category = update_main_category(
        category,
        serializer.validated_data,
    )

    response_serializer = CategoryDetailSerializer(
        category,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Category updated successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# UPDATE SUBCATEGORY
# ============================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_subcategory_view(
    request,
    subcategory_id,
):
    category = get_category(
        subcategory_id,
    )

    if category.parent_id is None:
        return Response(
            {
                "message": (
                    "This endpoint is only for subcategories."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = SubcategoryUpdateSerializer(
        category,
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True,
    )

    category = update_subcategory(
        category,
        serializer.validated_data,
    )

    response_serializer = CategoryDetailSerializer(
        category,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "message": "Subcategory updated successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# DELETE MAIN CATEGORY
# ============================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_category_view(
    request,
    category_id,
):
    category = get_category(
        category_id,
    )

    if category.parent_id is not None:
        return Response(
            {
                "message": (
                    "This endpoint is only for main categories."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    delete_category(
        category,
    )

    return Response(
        {
            "message": "Category deleted successfully.",
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# DELETE SUBCATEGORY
# ============================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_subcategory_view(
    request,
    subcategory_id,
):
    category = get_category(
        subcategory_id,
    )

    if category.parent_id is None:
        return Response(
            {
                "message": (
                    "This is a main category. "
                    "Use the category delete endpoint."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    delete_category(
        category,
    )

    return Response(
        {
            "message": "Subcategory deleted successfully.",
        },
        status=status.HTTP_200_OK,
    )