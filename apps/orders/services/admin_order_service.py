from decimal import Decimal

from django.db import transaction
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderItem


class AdminOrderService:

    @staticmethod
    def get_all_orders():
        return (
            Order.objects
            .select_related(
                "customer",
                "customer__user",
                "shipping_address",
            )
            .prefetch_related(
                "items",
                "items__variant",
                "items__variant__images",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_order_details(order_id):


        return (
            Order.objects
            .select_related(
                "customer",
                "customer__user",
                "shipping_address",
                "delivery_assignment",
                "delivery_assignment__delivery_partner",
                "delivery_assignment__delivery_partner__user",
            )
            .prefetch_related(
                "items",
                "items__variant",
                "items__variant__images",
            )
            .filter(
                id=order_id
            )
            .first()
        )

    @staticmethod
    @transaction.atomic
    def update_delivery_fee(order_id,delivery_fee,):
        try:
            order = (Order.objects.select_for_update().get(id=order_id))
        except Order.DoesNotExist:
            raise ValidationError({
                "order": "Order not found."
            })

        if order.status in [
            Order.Status.DELIVERED,
            Order.Status.CANCELLED,
        ]:
            raise ValidationError({
                "status": "Delivery fee cannot be changed for this order."
            })

        delivery_fee = Decimal(delivery_fee)

        # Recalculate total
        order.delivery_fee = delivery_fee

        order.total_amount = (
                order.subtotal
                + order.delivery_fee
                - order.discount
                + order.tax
        )

        order.save(
            update_fields=[
                "delivery_fee",
                "total_amount",
                "updated_at",
            ]
        )

        return order