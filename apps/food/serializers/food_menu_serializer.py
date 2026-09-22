from rest_framework import serializers

from apps.food.models.menu_category import MenuCategory
from apps.food.models.food_item import FoodItem
from apps.food.models.food_item_variant import FoodItemVariant
from apps.food.models.food_item_addon import FoodItemAddon


class FoodVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItemVariant
        fields = [
            "id",
            "name",
            "price",
            "is_default",
            "is_available",
            "display_order",
        ]
        read_only_fields = fields


class FoodAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItemAddon
        fields = [
            "id",
            "name",
            "price",
            "is_required",
            "max_quantity",
            "is_available",
            "display_order",
        ]
        read_only_fields = fields


class CustomerFoodItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    variants = FoodVariantSerializer(
        many=True,
        read_only=True,
    )

    addons = FoodAddonSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = FoodItem
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "image_url",
            "cloudinary_public_id",
            "food_type",
            "is_available",
            "is_bestseller",
            "is_recommended",
            "preparation_time",
            "display_order",
            "variants",
            "addons",
        ]
        read_only_fields = fields


class CustomerMenuCategorySerializer(serializers.ModelSerializer):
    food_item_count = serializers.IntegerField(
        source="food_items.count",
        read_only=True,
    )

    food_items = CustomerFoodItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = MenuCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image_url",
            "cloudinary_public_id",
            "display_order",
            "is_active",
            "food_item_count",
            "food_items",
        ]
        read_only_fields = fields


class CustomerFoodMenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image_url",
            "cloudinary_public_id",
            "display_order",
            "is_active",
        ]
        read_only_fields = fields