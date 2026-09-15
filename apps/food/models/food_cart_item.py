import uuid

from django.db import models


class FoodCartItem(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    cart = models.ForeignKey(
        "food.FoodCart",
        on_delete=models.CASCADE,
        related_name="items",
    )

    food_item = models.ForeignKey(
        "food.FoodItem",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    variant = models.ForeignKey(
        "food.FoodItemVariant",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "food_cart_items"

        ordering = ["created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"],
                name="unique_food_cart_variant",
            ),
        ]

    def __str__(self):
        return (
            f"{self.food_item.name} - "
            f"{self.variant.name} x {self.quantity}"
        )