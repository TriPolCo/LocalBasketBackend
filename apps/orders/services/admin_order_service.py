from django.db.models import Prefetch

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
            )
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=(
                        OrderItem.objects
                        .select_related(
                            "product",
                            "variant",
                        )
                        .prefetch_related(
                            "variant__images",
                        )
                        .order_by("created_at")
                    ),
                )
            )
            .filter(
                id=order_id
            )
            .first()
        )