from rest_framework import serializers

from apps.cart.models.cart import Cart
from apps.address.models.address import Address
from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderItem


class PlaceOrderSerializer(serializers.Serializer):

    cart_id = serializers.UUIDField(
        required=True,
    )

    address_id = serializers.UUIDField(
        required=True,
    )

    def validate_cart_id(self, value):

        if not Cart.objects.filter(
            id=value
        ).exists():
            raise serializers.ValidationError(
                "Cart not found."
            )

        return value

    def validate_address_id(self, value):

        if not Address.objects.filter(
            id=value
        ).exists():
            raise serializers.ValidationError(
                "Address not found."
            )

        return value


class OrderItemSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "variant",
            "product_name",
            "sku",
            "image",
            "quantity",
            "mrp",
            "selling_price",
            "item_discount",
            "item_total",
            "created_at",
        ]

        read_only_fields = fields

    def get_image(self, obj):
        image = (
            obj.variant.images
            .order_by("display_order", "created_at")
            .first()
        )

        if not image:
            return None

        return image.image_url

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",
            "status",

            "payment_method",
            "payment_status",

            "subtotal",
            "delivery_fee",
            "discount",
            "tax",
            "total_amount",

            "shipping_address",

            "items",

            "delivered_at",
            "cancelled_at",

            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_shipping_address(self, obj):

        return {
            "id": str(obj.shipping_address_id)
            if obj.shipping_address_id
            else None,

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