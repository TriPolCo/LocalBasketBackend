from rest_framework import serializers

from apps.food.models.menu_category import MenuCategory
from apps.food.models.food_item import FoodItem
from apps.food.models.food_item_variant import FoodItemVariant
from apps.food.models.food_item_addon import FoodItemAddon


# ============================================================
# FOOD VARIANT SERIALIZER
# ============================================================

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
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# FOOD ADDON SERIALIZER
# ============================================================

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
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# FOOD ITEM SERIALIZER
# ============================================================

class FoodItemSerializer(serializers.ModelSerializer):

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
            "is_active",
            "is_bestseller",
            "is_recommended",
            "preparation_time",
            "display_order",
            "variants",
            "addons",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "category_name",
            "variants",
            "addons",
            "created_at",
            "updated_at",
        ]


# ============================================================
# MENU CATEGORY CREATE SERIALIZER
# ============================================================

class MenuCategoryCreateSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=150,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    image_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    cloudinary_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    is_active = serializers.BooleanField(
        required=False,
        default=True,
    )

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Category name cannot be empty."
            )

        if MenuCategory.objects.filter(
            name__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "Menu category with this name already exists."
            )

        return value


# ============================================================
# MENU CATEGORY UPDATE SERIALIZER
# ============================================================

class MenuCategoryUpdateSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=150,
        required=False,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    image_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    cloudinary_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
    )

    is_active = serializers.BooleanField(
        required=False,
    )

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Category name cannot be empty."
            )

        return value


# ============================================================
# MENU CATEGORY RESPONSE SERIALIZER
# ============================================================

class MenuCategorySerializer(serializers.ModelSerializer):

    food_item_count = serializers.IntegerField(
        source="food_items.count",
        read_only=True,
    )

    food_items = FoodItemSerializer(
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
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "food_item_count",
            "food_items",
            "created_at",
            "updated_at",
        ]