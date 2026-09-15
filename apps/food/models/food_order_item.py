import uuid

from django.db import models


class FoodOrderItem(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        "food.FoodOrder",
        on_delete=models.CASCADE,
        related_name="items",
    )

    # ==============================
    # ORIGINAL REFERENCES
    # ==============================

    food_item = models.ForeignKey(
        "food.FoodItem",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    variant = models.ForeignKey(
        "food.FoodItemVariant",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # ==============================
    # FOOD ITEM SNAPSHOT
    # ==============================

    food_name = models.CharField(
        max_length=255,
    )

    food_type = models.CharField(
        max_length=20,
    )

    food_image_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
    )

    # ==============================
    # VARIANT SNAPSHOT
    # ==============================

    variant_name = models.CharField(
        max_length=100,
    )

    # ==============================
    # PRICE SNAPSHOT
    # ==============================

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    # ==============================
    # QUANTITY
    # ==============================

    quantity = models.PositiveIntegerField(
        default=1,
    )

    # ==============================
    # ADDON / TOTAL SNAPSHOT
    # ==============================

    addon_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    item_total = models.DecimalField(
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
        db_table = "food_order_items"

        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["order"],
                name="foi_order_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.food_name} - "
            f"{self.variant_name} x {self.quantity}"
        )