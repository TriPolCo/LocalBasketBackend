from decimal import Decimal

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
        if not obj.variant:
            return None

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
            "order_type",

            # Express List Order Details (Upload Image / Typed List)
            "list_image_url",
            "list_text_content",
            "special_instructions",
            "manual_items",

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
        if not obj.customer:
            return None

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


class AdminOrderItemDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "sku",
            "quantity",
            "mrp",
            "selling_price",
            "item_discount",
            "item_total",
        ]


class AdminUpdateDeliveryFeeSerializer(serializers.Serializer):

    delivery_fee = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )


class ManualBillItemSerializer(serializers.Serializer):

    quantity_label = serializers.CharField(
        max_length=50,
        default="1 pc",
    )
    product_name = serializers.CharField(
        max_length=255,
    )
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )


class AdminSaveExpressBillSerializer(serializers.Serializer):

    items = ManualBillItemSerializer(many=True)
    discount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
        default=Decimal("0.00"),
    )
    delivery_fee = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
    )