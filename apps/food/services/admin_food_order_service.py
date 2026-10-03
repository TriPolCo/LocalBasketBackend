from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from apps.food.models.food_order import FoodOrder

from apps.delivery.services import (
    DeliveryAssignmentService,
)


class AdminFoodOrderService:

    # ==========================================================
    # GET ALL ORDERS
    # ==========================================================

    @staticmethod
    def get_orders(
        status_value=None,
        search=None,
    ):

        queryset = (
            FoodOrder.objects
            .select_related(
                "customer",
                "customer__user",
            )
            .prefetch_related(
                "items__addons",
                "delivery_assignment",
                "delivery_assignment__delivery_partner",
                "delivery_assignment__delivery_partner__user",
            )
            .order_by(
                "-created_at"
            )
        )

        # ------------------------------------------------------
        # STATUS FILTER
        # ------------------------------------------------------

        if status_value:

            queryset = queryset.filter(
                status=status_value
            )

        # ------------------------------------------------------
        # SEARCH
        # ------------------------------------------------------

        if search:

            queryset = queryset.filter(
                order_number__icontains=search
            )

        return queryset

    # ==========================================================
    # GET SINGLE ORDER
    # ==========================================================

    @staticmethod
    def get_order(
        order_id,
    ):

        try:

            return (
                FoodOrder.objects
                .select_related(
                    "customer",
                    "customer__user",
                )
                .prefetch_related(
                    "items__addons",
                    "delivery_assignment",
                    "delivery_assignment__delivery_partner",
                    "delivery_assignment__delivery_partner__user",
                )
                .get(
                    id=order_id
                )
            )

        except FoodOrder.DoesNotExist:

            raise ValidationError({
                "order": "Food order not found."
            })

    # ==========================================================
    # UPDATE ORDER STATUS
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def update_status(
        order_id,
        new_status,
    ):

        try:

            order = (
                FoodOrder.objects
                .select_for_update()
                .get(
                    id=order_id
                )
            )

        except FoodOrder.DoesNotExist:

            raise ValidationError({
                "order": "Food order not found."
            })

        # ------------------------------------------------------
        # VALID STATUS
        # ------------------------------------------------------

        valid_statuses = dict(
            FoodOrder.Status.choices
        )

        if new_status not in valid_statuses:

            raise ValidationError({
                "status": "Invalid food order status."
            })

        # ------------------------------------------------------
        # ALREADY DELIVERED
        # ------------------------------------------------------

        if (
            order.status
            == FoodOrder.Status.DELIVERED
        ):

            raise ValidationError({
                "status":
                    "Delivered order cannot be changed."
            })

        # ------------------------------------------------------
        # ALREADY CANCELLED
        # ------------------------------------------------------

        if (
            order.status
            == FoodOrder.Status.CANCELLED
        ):

            raise ValidationError({
                "status":
                    "Cancelled order cannot be changed."
            })

        # ------------------------------------------------------
        # UPDATE STATUS
        # ------------------------------------------------------

        order.status = new_status

        update_fields = [
            "status",
            "updated_at",
        ]

        # ------------------------------------------------------
        # DELIVERED
        # ------------------------------------------------------

        if (
            new_status
            == FoodOrder.Status.DELIVERED
        ):

            order.delivered_at = (
                timezone.now()
            )

            update_fields.append(
                "delivered_at"
            )

        # ------------------------------------------------------
        # CANCELLED
        # ------------------------------------------------------

        if (
            new_status
            == FoodOrder.Status.CANCELLED
        ):

            order.cancelled_at = (
                timezone.now()
            )

            update_fields.append(
                "cancelled_at"
            )

        # ------------------------------------------------------
        # SAVE
        # ------------------------------------------------------

        order.save(
            update_fields=update_fields
        )

        return order

    # ==========================================================
    # UPDATE DELIVERY FEE
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def update_delivery_fee(
        order_id,
        delivery_fee,
    ):

        try:

            order = (
                FoodOrder.objects
                .select_for_update()
                .get(
                    id=order_id
                )
            )

        except FoodOrder.DoesNotExist:

            raise ValidationError({
                "order": "Food order not found."
            })

        # ------------------------------------------------------
        # CONVERT DELIVERY FEE
        # ------------------------------------------------------

        try:

            delivery_fee = Decimal(
                str(delivery_fee)
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValidationError({
                "delivery_fee":
                    "Invalid delivery fee."
            })

        # ------------------------------------------------------
        # NEGATIVE FEE
        # ------------------------------------------------------

        if delivery_fee < 0:

            raise ValidationError({
                "delivery_fee":
                    "Delivery fee cannot be negative."
            })

        # ------------------------------------------------------
        # DELIVERED ORDER
        # ------------------------------------------------------

        if (
            order.status
            == FoodOrder.Status.DELIVERED
        ):

            raise ValidationError({
                "order":
                    "Cannot update delivery fee for a delivered order."
            })

        # ------------------------------------------------------
        # CANCELLED ORDER
        # ------------------------------------------------------

        if (
            order.status
            == FoodOrder.Status.CANCELLED
        ):

            raise ValidationError({
                "order":
                    "Cannot update delivery fee for a cancelled order."
            })

        # ------------------------------------------------------
        # UPDATE DELIVERY FEE
        # ------------------------------------------------------

        order.delivery_fee = delivery_fee

        # ------------------------------------------------------
        # RECALCULATE TOTAL
        #
        # total =
        # subtotal
        # + delivery_fee
        # + packaging_fee
        # + tax
        # - discount
        # ------------------------------------------------------

        order.total_amount = (
            order.subtotal
            + order.delivery_fee
            + order.packaging_fee
            + order.tax
            - order.discount
        )

        # ------------------------------------------------------
        # SAVE
        # ------------------------------------------------------

        order.save(
            update_fields=[
                "delivery_fee",
                "total_amount",
                "updated_at",
            ]
        )

        return order

    # ==========================================================
    # ASSIGN DELIVERY PARTNER
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def assign_delivery_partner(
        order_id,
        delivery_partner_id,
    ):

        # ------------------------------------------------------
        # MAKE SURE ORDER EXISTS
        # ------------------------------------------------------

        order = (
            AdminFoodOrderService
            .get_order(
                order_id
            )
        )

        # ------------------------------------------------------
        # CANNOT ASSIGN DELIVERED ORDER
        # ------------------------------------------------------

        if (
            order.status
            == FoodOrder.Status.DELIVERED
        ):

            raise ValidationError({
                "order":
                    "Cannot assign delivery to a delivered order."
            })

        # ------------------------------------------------------
        # CANNOT ASSIGN CANCELLED ORDER
        # ------------------------------------------------------

        if (
            order.status
            == FoodOrder.Status.CANCELLED
        ):

            raise ValidationError({
                "order":
                    "Cannot assign delivery to a cancelled order."
            })

        # ------------------------------------------------------
        # ASSIGN DELIVERY
        # ------------------------------------------------------

        assignment = (
            DeliveryAssignmentService
            .assign_food_order(
                food_order_id=order_id,
                delivery_partner_id=(
                    delivery_partner_id
                ),
            )
        )

        return assignment