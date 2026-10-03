from rest_framework import serializers

from apps.food.models.food_order import FoodOrder
from apps.delivery.models.delivery_assignment import (
    DeliveryAssignment,
)


# ==========================================================
# UPDATE FOOD ORDER DELIVERY FEE
# ==========================================================

class UpdateFoodDeliveryFeeSerializer(
    serializers.Serializer
):

    delivery_fee = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )


# ==========================================================
# ADMIN - CUSTOMER
# ==========================================================

class AdminFoodOrderCustomerSerializer(
    serializers.Serializer
):

    id = serializers.UUIDField(
        read_only=True
    )

    name = serializers.SerializerMethodField()

    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    def get_name(
        self,
        obj,
    ):

        user = obj.user

        return (
            f"{user.first_name or ''} "
            f"{user.last_name or ''}"
        ).strip()


# ==========================================================
# ADMIN - DELIVERY PARTNER
# ==========================================================

class AdminFoodDeliveryPartnerSerializer(
    serializers.Serializer
):

    id = serializers.UUIDField(
        read_only=True
    )

    name = serializers.SerializerMethodField()

    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    def get_name(
        self,
        obj,
    ):

        user = obj.user

        return (
            f"{user.first_name or ''} "
            f"{user.last_name or ''}"
        ).strip()


# ==========================================================
# ADMIN - DELIVERY ASSIGNMENT
# ==========================================================

class AdminFoodDeliverySerializer(
    serializers.ModelSerializer
):

    delivery_partner = (
        AdminFoodDeliveryPartnerSerializer(
            read_only=True
        )
    )

    class Meta:

        model = DeliveryAssignment

        fields = [
            "id",
            "status",
            "delivery_partner",
            "payment_method",
            "payment_confirmed",
            "delivery_image_url",
            "delivery_image_public_id",
            "assigned_at",
            "accepted_at",
            "started_at",
            "delivered_at",
            "cancelled_at",
            "updated_at",
        ]

        read_only_fields = fields


# ==========================================================
# ADMIN - FOOD ORDER
# ==========================================================

class AdminFoodOrderSerializer(
    serializers.ModelSerializer
):

    customer = (
        serializers.SerializerMethodField()
    )

    items = serializers.SerializerMethodField()

    pricing = (
        serializers.SerializerMethodField()
    )

    shipping_address = (
        serializers.SerializerMethodField()
    )

    delivery = (
        serializers.SerializerMethodField()
    )

    class Meta:

        model = FoodOrder

        fields = [
            "id",
            "order_number",
            "status",

            "payment_method",
            "payment_status",

            "customer",

            "pricing",

            "shipping_address",

            "customer_note",

            "items",

            "delivery",

            "delivered_at",
            "cancelled_at",

            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    # ======================================================
    # CUSTOMER
    # ======================================================

    def get_customer(
        self,
        obj,
    ):

        return AdminFoodOrderCustomerSerializer(
            obj.customer
        ).data

    # ======================================================
    # ITEMS
    # ======================================================

    def get_items(
        self,
        obj,
    ):

        from apps.food.serializers.food_order_serializer import (
            FoodOrderItemSerializer,
        )

        return FoodOrderItemSerializer(
            obj.items.all(),
            many=True,
        ).data

    # ======================================================
    # PRICING
    # ======================================================

    def get_pricing(
        self,
        obj,
    ):

        return {
            "subtotal": str(
                obj.subtotal
            ),

            "delivery_fee": str(
                obj.delivery_fee
            ),

            "packaging_fee": str(
                obj.packaging_fee
            ),

            "discount": str(
                obj.discount
            ),

            "tax": str(
                obj.tax
            ),

            "total_amount": str(
                obj.total_amount
            ),
        }

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    def get_shipping_address(
        self,
        obj,
    ):

        return {
            "full_name": (
                obj.shipping_full_name
            ),

            "phone_number": (
                obj.shipping_phone_number
            ),

            "address_line_1": (
                obj.shipping_address_line_1
            ),

            "address_line_2": (
                obj.shipping_address_line_2
            ),

            "landmark": (
                obj.shipping_landmark
            ),

            "city": (
                obj.shipping_city
            ),

            "state": (
                obj.shipping_state
            ),

            "postal_code": (
                obj.shipping_postal_code
            ),

            "country": (
                obj.shipping_country
            ),
        }

    # ======================================================
    # DELIVERY
    # ======================================================

    def get_delivery(
        self,
        obj,
    ):

        try:

            assignment = (
                obj.delivery_assignment
            )

        except DeliveryAssignment.DoesNotExist:

            return None

        return AdminFoodDeliverySerializer(
            assignment
        ).data