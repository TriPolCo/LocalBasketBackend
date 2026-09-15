from rest_framework import serializers

from apps.food.models.food_cart import FoodCart
from apps.food.models.food_cart_item import FoodCartItem
from apps.food.models.food_cart_item_addon import FoodCartItemAddon


class FoodCartAddonInputSerializer(serializers.Serializer):
    addon_id = serializers.UUIDField()
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )


class AddFoodToCartSerializer(serializers.Serializer):
    food_item_id = serializers.UUIDField()
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )
    addons = FoodCartAddonInputSerializer(
        many=True,
        required=False,
        default=list,
    )


class UpdateFoodCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    addons = FoodCartAddonInputSerializer(
        many=True,
        required=False,
    )


class FoodCartItemAddonSerializer(serializers.ModelSerializer):
    addon_name = serializers.CharField(
        source="addon.name",
        read_only=True,
    )

    price = serializers.DecimalField(
        source="addon.price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = FoodCartItemAddon
        fields = [
            "id",
            "addon",
            "addon_name",
            "price",
            "quantity",
        ]
        read_only_fields = fields


class FoodCartItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(
        source="food_item.name",
        read_only=True,
    )

    food_image_url = serializers.CharField(
        source="food_item.image_url",
        read_only=True,
    )

    variant_name = serializers.CharField(
        source="variant.name",
        read_only=True,
    )

    unit_price = serializers.DecimalField(
        source="variant.price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    addons = FoodCartItemAddonSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = FoodCartItem
        fields = [
            "id",
            "food_item",
            "food_name",
            "food_image_url",
            "variant",
            "variant_name",
            "unit_price",
            "quantity",
            "addons",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class FoodCartSerializer(serializers.ModelSerializer):
    items = FoodCartItemSerializer(
        source="items",
        many=True,
        read_only=True,
    )

    class Meta:
        model = FoodCart
        fields = [
            "id",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields