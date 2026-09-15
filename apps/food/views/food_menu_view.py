from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.food.serializers.food_menu_serializer import (
    CustomerMenuCategorySerializer,
    CustomerFoodItemSerializer,
)
from apps.food.services.food_menu_service import FoodMenuService


@api_view(["GET"])
@permission_classes([AllowAny])
def get_food_categories(request):

    categories = FoodMenuService.get_categories()

    serializer = CustomerMenuCategorySerializer(
        categories,
        many=True,
    )

    return Response({
        "success": True,
        "message": "Food categories fetched successfully.",
        "data": serializer.data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def get_food_category(request, category_id):

    category = FoodMenuService.get_category(
        category_id
    )

    serializer = CustomerMenuCategorySerializer(
        category
    )

    return Response({
        "success": True,
        "message": "Food category fetched successfully.",
        "data": serializer.data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def get_food_items(request):

    params = {
        "category": request.query_params.get("category"),
        "food_type": request.query_params.get("food_type"),
        "search": request.query_params.get("search"),
    }

    if request.query_params.get("is_bestseller") is not None:
        params["is_bestseller"] = (
            request.query_params.get("is_bestseller").lower()
            == "true"
        )

    if request.query_params.get("is_recommended") is not None:
        params["is_recommended"] = (
            request.query_params.get("is_recommended").lower()
            == "true"
        )

    items = FoodMenuService.get_food_items(params)

    serializer = CustomerFoodItemSerializer(
        items,
        many=True,
    )

    return Response({
        "success": True,
        "message": "Food items fetched successfully.",
        "data": serializer.data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def get_food_item(request, food_item_id):

    item = FoodMenuService.get_food_item(
        food_item_id
    )

    serializer = CustomerFoodItemSerializer(item)

    return Response({
        "success": True,
        "message": "Food item fetched successfully.",
        "data": serializer.data,
    })