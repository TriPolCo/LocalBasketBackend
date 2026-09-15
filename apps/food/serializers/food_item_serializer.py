from django.utils.text import slugify
from rest_framework import serializers

from apps.food.models.food_item import FoodItem
from apps.food.models.food_item_variant import FoodItemVariant
from apps.food.models.food_item_addon import FoodItemAddon
from apps.food.models.menu_category import MenuCategory


class FoodVariantCreateSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=100,
    )

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    is_default = serializers.BooleanField(
        required=False,
        default=False,
    )

    is_available = serializers.BooleanField(
        required=False,
        default=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )


class FoodAddonCreateSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=150,
    )

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    is_required = serializers.BooleanField(
        required=False,
        default=False,
    )

    max_quantity = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    is_available = serializers.BooleanField(
        required=False,
        default=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )


class FoodItemCreateSerializer(serializers.Serializer):

    category = serializers.UUIDField()

    name = serializers.CharField(
        max_length=255,
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

    food_type = serializers.ChoiceField(
        choices=FoodItem.FoodType.choices,
    )

    is_available = serializers.BooleanField(
        required=False,
        default=True,
    )

    is_active = serializers.BooleanField(
        required=False,
        default=True,
    )

    is_bestseller = serializers.BooleanField(
        required=False,
        default=False,
    )

    is_recommended = serializers.BooleanField(
        required=False,
        default=False,
    )

    preparation_time = serializers.IntegerField(
        required=False,
        min_value=1,
        allow_null=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    variants = FoodVariantCreateSerializer(
        many=True,
        required=True,
    )

    addons = FoodAddonCreateSerializer(
        many=True,
        required=False,
        default=list,
    )

    def validate_category(self, value):

        if not MenuCategory.objects.filter(
            id=value,
            is_active=True,
        ).exists():
            raise serializers.ValidationError(
                "Menu category not found or inactive."
            )

        return value

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Food item name cannot be empty."
            )

        return value

    def validate_variants(self, value):

        if not value:
            raise serializers.ValidationError(
                "At least one variant is required."
            )

        default_count = sum(
            1
            for variant in value
            if variant.get("is_default") is True
        )

        if default_count > 1:
            raise serializers.ValidationError(
                "Only one variant can be default."
            )

        return value




class FoodVariantUpdateSerializer(serializers.Serializer):

    id = serializers.UUIDField(
        required=False,
    )

    name = serializers.CharField(
        max_length=100,
    )

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    is_default = serializers.BooleanField(
        required=False,
        default=False,
    )

    is_available = serializers.BooleanField(
        required=False,
        default=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )


class FoodAddonUpdateSerializer(serializers.Serializer):

    id = serializers.UUIDField(
        required=False,
    )

    name = serializers.CharField(
        max_length=150,
    )

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    is_required = serializers.BooleanField(
        required=False,
        default=False,
    )

    max_quantity = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    is_available = serializers.BooleanField(
        required=False,
        default=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )


class FoodItemUpdateSerializer(serializers.Serializer):

    category = serializers.UUIDField(
        required=False,
    )

    name = serializers.CharField(
        max_length=255,
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

    food_type = serializers.ChoiceField(
        choices=FoodItem.FoodType.choices,
        required=False,
    )

    is_available = serializers.BooleanField(
        required=False,
    )

    is_active = serializers.BooleanField(
        required=False,
    )

    is_bestseller = serializers.BooleanField(
        required=False,
    )

    is_recommended = serializers.BooleanField(
        required=False,
    )

    preparation_time = serializers.IntegerField(
        required=False,
        min_value=1,
        allow_null=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
    )

    variants = FoodVariantUpdateSerializer(
        many=True,
        required=False,
    )

    addons = FoodAddonUpdateSerializer(
        many=True,
        required=False,
    )



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