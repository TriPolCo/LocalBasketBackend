from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin

from apps.food.serializers.menu_category_serializer import (
    MenuCategoryCreateSerializer,
    MenuCategoryUpdateSerializer,
    MenuCategorySerializer,
)

from apps.food.serializers.food_item_serializer import (
    FoodItemCreateSerializer,
    FoodItemUpdateSerializer,
    FoodItemSerializer,
)

from apps.food.services.menu_service import MenuService



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_get_menu_categories(request):

    categories = MenuService.get_categories()

    serializer = MenuCategorySerializer(
        categories,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Menu categories fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_create_menu_category(request):

    serializer = MenuCategoryCreateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    category = MenuService.create_category(
        **serializer.validated_data
    )

    response_serializer = MenuCategorySerializer(
        category
    )

    return Response(
        {
            "success": True,
            "message": "Menu category created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_get_menu_category(
    request,
    category_id,
):

    category = MenuService.get_category(
        category_id
    )

    serializer = MenuCategorySerializer(
        category
    )

    return Response(
        {
            "success": True,
            "message": "Menu category fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_menu_category(
    request,
    category_id,
):

    serializer = MenuCategoryUpdateSerializer(
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True
    )

    category = MenuService.update_category(
        category_id=category_id,
        **serializer.validated_data
    )

    response_serializer = MenuCategorySerializer(
        category
    )

    return Response(
        {
            "success": True,
            "message": "Menu category updated successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )



@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_menu_category(
    request,
    category_id,
):

    MenuService.delete_category(
        category_id
    )

    return Response(
        {
            "success": True,
            "message": "Menu category deleted successfully.",
            "data": None,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_get_food_items(request):

    food_items = MenuService.get_food_items()

    serializer = FoodItemSerializer(
        food_items,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Food items fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )



@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_create_food_item(request):

    serializer = FoodItemCreateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    food_item = MenuService.create_food_item(
        **serializer.validated_data
    )

    response_serializer = FoodItemSerializer(
        food_item
    )

    return Response(
        {
            "success": True,
            "message": "Food item created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_get_food_item(
    request,
    food_item_id,
):

    food_item = MenuService.get_food_item(
        food_item_id
    )

    serializer = FoodItemSerializer(
        food_item
    )

    return Response(
        {
            "success": True,
            "message": "Food item fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_food_item(
    request,
    food_item_id,
):

    serializer = FoodItemUpdateSerializer(
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True
    )

    food_item = MenuService.update_food_item(
        food_item_id=food_item_id,
        **serializer.validated_data
    )

    response_serializer = FoodItemSerializer(
        food_item
    )

    return Response(
        {
            "success": True,
            "message": "Food item updated successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_food_item(
    request,
    food_item_id,
):

    food_item = MenuService.delete_food_item(
        food_item_id
    )

    if food_item:

        serializer = FoodItemSerializer(
            food_item
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Food item has been deactivated "
                    "because it is used in order history."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "success": True,
            "message": "Food item deleted successfully.",
            "data": None,
        },
        status=status.HTTP_200_OK,
    )