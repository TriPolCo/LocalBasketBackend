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

        if not order_id and not food_order_id:
            raise serializers.ValidationError({
                "order": "Either order_id or food_order_id is required."
            })

        if order_id and food_order_id:
            raise serializers.ValidationError({
                "order": "Provide either order_id or food_order_id, not both."
            })

        return attrs


# ==========================================================
# DELIVERY ASSIGNMENT RESPONSE
# ==========================================================

class DeliveryAssignmentSerializer(
    serializers.ModelSerializer
):

    delivery_partner_id = serializers.UUIDField(
        source="delivery_partner.id",
        read_only=True,
    )

    delivery_partner_name = serializers.SerializerMethodField()

    delivery_partner_phone = serializers.CharField(
        source="delivery_partner.user.phone_number",
        read_only=True,
    )

    order_id = serializers.UUIDField(
        source="order.id",
        read_only=True,
        allow_null=True,
    )

    food_order_id = serializers.UUIDField(
        source="food_order.id",
        read_only=True,
        allow_null=True,
    )

    order_category = serializers.SerializerMethodField()
    order_details = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryAssignment

        fields = [
            "id",

            # Order
            "order_id",
            "food_order_id",
            "order_category",
            "order_details",

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

    def get_delivery_partner_name(self, obj):
        user = obj.delivery_partner.user
        return f"{user.first_name or ''} {user.last_name or ''}".strip()

    def get_order_category(self, obj):
        return "FOOD" if obj.food_order_id else "GROCERY"

    def _extract_address_data(self, target_order):
        # 1. Prefer snapshot fields stored directly on Order (same as Invoice PDF)
        line_1 = getattr(target_order, "shipping_address_line_1", None)
        line_2 = getattr(target_order, "shipping_address_line_2", None)
        landmark = getattr(target_order, "shipping_landmark", None)
        city = getattr(target_order, "shipping_city", None)
        state = getattr(target_order, "shipping_state", None)
        postal_code = getattr(target_order, "shipping_postal_code", None)
        country = getattr(target_order, "shipping_country", None)

        # 2. Fallback to related shipping_address / delivery_address object
        if not any([line_1, city, postal_code]):
            addr = (
                getattr(target_order, "shipping_address", None)
                or getattr(target_order, "address", None)
                or getattr(target_order, "delivery_address", None)
            )
            if isinstance(addr, str):
                line_1 = addr
            elif addr is not None:
                line_1 = (
                    getattr(addr, "address_line_1", None)
                    or getattr(addr, "address_line1", None)
                    or getattr(addr, "street", None)
                    or getattr(addr, "full_address", None)
                )
                line_2 = (
                    getattr(addr, "address_line_2", None)
                    or getattr(addr, "address_line2", None)
                )
                landmark = getattr(addr, "landmark", None)
                city = getattr(addr, "city", None)
                state = getattr(addr, "state", None)
                postal_code = (
                    getattr(addr, "postal_code", None)
                    or getattr(addr, "pincode", None)
                )
                country = getattr(addr, "country", None)

        city_state = ", ".join([p.strip() for p in [city, state] if p and str(p).strip()])
        if city_state and postal_code:
            city_line = f"{city_state} - {str(postal_code).strip()}"
        else:
            city_line = city_state or (str(postal_code).strip() if postal_code else "")

        formatted_parts = [
            str(line_1).strip() if line_1 else "",
            str(line_2).strip() if line_2 else "",
            f"Landmark: {str(landmark).strip()}" if landmark else "",
            city_line,
        ]
        formatted = ", ".join([p for p in formatted_parts if p])

        return {
            "formatted": formatted or None,
            "line_1": str(line_1).strip() if line_1 else None,
            "line_2": str(line_2).strip() if line_2 else None,
            "landmark": str(landmark).strip() if landmark else None,
            "city": str(city).strip() if city else None,
            "state": str(state).strip() if state else None,
            "postal_code": str(postal_code).strip() if postal_code else None,
            "country": str(country).strip() if country else None,
        }

    def get_order_details(self, obj):
        target = obj.order or obj.food_order
        if not target:
            return None

        customer_obj = (
            getattr(target, "customer", None)
            or getattr(target, "user", None)
        )
        user_obj = (
            getattr(customer_obj, "user", None)
            or customer_obj
        )

        shipping = (
            getattr(target, "shipping_address", None)
            or getattr(target, "address", None)
            or getattr(target, "delivery_address", None)
        )

        # Prefer snapshot shipping_full_name & shipping_phone_number on Order
        customer_name = (getattr(target, "shipping_full_name", None) or "").strip()
        customer_phone = getattr(target, "shipping_phone_number", None)

        if not customer_name and shipping:
            customer_name = (getattr(shipping, "full_name", None) or "").strip()

        if not customer_name and user_obj:
            customer_name = (
                f"{getattr(user_obj, 'first_name', '') or ''} "
                f"{getattr(user_obj, 'last_name', '') or ''}"
            ).strip()

        if not customer_phone and shipping:
            customer_phone = (
                getattr(shipping, "phone_number", None)
                or getattr(shipping, "phone", None)
            )

        if not customer_phone and user_obj:
            customer_phone = getattr(user_obj, "phone_number", None)

        total_amount = (
            getattr(target, "total_amount", None)
            or getattr(target, "grand_total", None)
            or getattr(target, "total", 0)
        )

        items_count = 0
        if hasattr(target, "items"):
            try:
                items_count = target.items.count()
            except Exception:
                items_count = 0

        manual_items = getattr(target, "manual_items", None)
        if items_count == 0 and isinstance(manual_items, list):
            items_count = len(manual_items)

        address_data = self._extract_address_data(target)

        return {
            "order_number": getattr(target, "order_number", str(target.id)[:8].upper()),
            "order_status": getattr(target, "status", None),
            "order_type": getattr(target, "order_type", "FOOD" if obj.food_order_id else "REGULAR"),
            "customer_name": customer_name or "Customer",
            "customer_phone": str(customer_phone).strip() if customer_phone else None,
            "delivery_address": address_data["formatted"],
            "address": address_data,
            "total_amount": float(total_amount or 0),
            "payment_method": getattr(target, "payment_method", None),
            "payment_status": getattr(target, "payment_status", None),
            "items_count": items_count,
            "special_instructions": getattr(target, "special_instructions", None),
            "created_at": getattr(target, "created_at", None),
        }


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