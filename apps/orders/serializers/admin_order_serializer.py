from rest_framework import serializers

from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderItem


class AdminOrderItemSerializer(serializers.ModelSerializer):

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

    def get_image(self, obj):
        image = (
            obj.variant.images
            .order_by("display_order", "created_at")
            .first()
        )

        return image.image_url if image else None


class AdminOrderSerializer(serializers.ModelSerializer):

    customer = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    items = AdminOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",

            "customer",

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

    def get_customer(self, obj):
        user = obj.customer.user

        return {
            "id": str(obj.customer.id),
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
        }

    def get_shipping_address(self, obj):
        return {
            "id": (
                str(obj.shipping_address_id)
                if obj.shipping_address_id
                else None
            ),
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