from rest_framework import serializers

from apps.food.models.food_order import FoodOrder
from apps.food.models.food_order_item import FoodOrderItem
from apps.food.models.food_order_item_addon import FoodOrderItemAddon


class FoodOrderPlaceSerializer(serializers.Serializer):
    address_id = serializers.UUIDField()

    payment_method = serializers.ChoiceField(
        choices=FoodOrder.PaymentMethod.choices,
        default=FoodOrder.PaymentMethod.COD,
    )

    customer_note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


class FoodOrderItemAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOrderItemAddon
        fields = [
            "id",
            "addon_name",
            "unit_price",
            "quantity",
            "total_amount",
        ]
        read_only_fields = fields


class FoodOrderItemSerializer(serializers.ModelSerializer):
    addons = FoodOrderItemAddonSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = FoodOrderItem
        fields = [
            "id",
            "food_item",
            "variant",
            "food_name",
            "food_type",
            "food_image_url",
            "variant_name",
            "unit_price",
            "quantity",
            "addon_total",
            "item_total",
            "addons",
        ]
        read_only_fields = fields


class FoodOrderSerializer(serializers.ModelSerializer):
    items = FoodOrderItemSerializer(
        many=True,
        read_only=True,
    )

    pricing = serializers.SerializerMethodField()

    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = FoodOrder
        fields = [
            "id",
            "order_number",
            "status",
            "payment_method",
            "payment_status",
            "pricing",
            "shipping_address",
            "customer_note",
            "delivered_at",
            "cancelled_at",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_pricing(self, obj):
        return {
            "subtotal": str(obj.subtotal),
            "delivery_fee": str(obj.delivery_fee),
            "packaging_fee": str(obj.packaging_fee),
            "discount": str(obj.discount),
            "tax": str(obj.tax),
            "total_amount": str(obj.total_amount),
        }

    def get_shipping_address(self, obj):
        return {
            "full_name": obj.shipping_full_name,
            "phone_number": obj.shipping_phone_number,
            "address_line_1": obj.shipping_address_line_1,
            "address_line_2": obj.shipping_address_line_2,
            "landmark": obj.shipping_landmark,
            "city": obj.shipping_city,
            "state": obj.shipping_state,
            "postal_code": obj.shipping_postal_code,
            "country": obj.shipping_country,
        }