from apps.orders.models.order import Order


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