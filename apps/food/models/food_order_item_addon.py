import uuid

from django.db import models


class FoodOrderItemAddon(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order_item = models.ForeignKey(
        "food.FoodOrderItem",
        on_delete=models.CASCADE,
        related_name="addons",
    )

    # ==============================
    # ORIGINAL ADDON REFERENCE
    # ==============================

    addon = models.ForeignKey(
        "food.FoodItemAddon",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # ==============================
    # ADDON SNAPSHOT
    # ==============================

    addon_name = models.CharField(
        max_length=150,
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "food_order_item_addons"

        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["order_item"],
                name="foia_order_item_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.addon_name} x {self.quantity}"
        )