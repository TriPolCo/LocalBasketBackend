from rest_framework import serializers

from apps.delivery.models.delivery_assignment import (
    DeliveryAssignment,
)


# ==========================================================
# CREATE DELIVERY ASSIGNMENT
# ==========================================================

class DeliveryAssignmentCreateSerializer(
    serializers.Serializer
):

    order_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    food_order_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    delivery_partner_id = serializers.UUIDField()

    def validate(self, attrs):

        order_id = attrs.get("order_id")
        food_order_id = attrs.get("food_order_id")

        # Exactly one order type must be provided
        if not order_id and not food_order_id:
            raise serializers.ValidationError({
                "order":
                    "Either order_id or food_order_id is required."
            })

        if order_id and food_order_id:
            raise serializers.ValidationError({
                "order":
                    "Provide either order_id or food_order_id, not both."
            })

        return attrs


# ==========================================================
# DELIVERY ASSIGNMENT RESPONSE
# ==========================================================

class DeliveryAssignmentSerializer(
    serializers.ModelSerializer
):

    # ------------------------------------------------------
    # Delivery Partner
    # ------------------------------------------------------

    delivery_partner_id = serializers.UUIDField(
        source="delivery_partner.id",
        read_only=True,
    )

    delivery_partner_name = (
        serializers.SerializerMethodField()
    )

    delivery_partner_phone = serializers.CharField(
        source="delivery_partner.user.phone_number",
        read_only=True,
    )

    # ------------------------------------------------------
    # Normal Order
    # ------------------------------------------------------

    order_id = serializers.UUIDField(
        source="order.id",
        read_only=True,
        allow_null=True,
    )

    # ------------------------------------------------------
    # Food Order
    # ------------------------------------------------------

    food_order_id = serializers.UUIDField(
        source="food_order.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:

        model = DeliveryAssignment

        fields = [
            "id",

            # Order
            "order_id",
            "food_order_id",

            # Delivery partner
            "delivery_partner_id",
            "delivery_partner_name",
            "delivery_partner_phone",

            # Assignment
            "status",

            # Payment
            "payment_method",
            "payment_confirmed",

            # Delivery proof
            "delivery_image_url",
            "delivery_image_public_id",

            # Timestamps
            "assigned_at",
            "accepted_at",
            "started_at",
            "delivered_at",
            "cancelled_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_delivery_partner_name(
        self,
        obj
    ):

        user = obj.delivery_partner.user

        return (
            f"{user.first_name or ''} "
            f"{user.last_name or ''}"
        ).strip()


# ==========================================================
# DELIVERY PROOF
# ==========================================================

class DeliveryProofSerializer(
    serializers.Serializer
):

    delivery_image_url = serializers.URLField(
        max_length=1000,
    )

    delivery_image_public_id = serializers.CharField(
        max_length=500,
    )

    payment_method = serializers.ChoiceField(
        choices=DeliveryAssignment.PaymentMethod.choices
    )

    payment_confirmed = serializers.BooleanField(
        required=False,
        default=False,
    )