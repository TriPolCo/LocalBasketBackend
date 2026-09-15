import uuid

from django.db import models


class FoodCartItemAddon(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    cart_item = models.ForeignKey(
        "food.FoodCartItem",
        on_delete=models.CASCADE,
        related_name="addons",
    )

    addon = models.ForeignKey(
        "food.FoodItemAddon",
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
        db_table = "food_cart_item_addons"

        ordering = [
            "created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart_item",
                    "addon",
                ],
                name="unique_food_cart_item_addon",
            ),
        ]

    def __str__(self):
        return (
            f"{self.cart_item.food_item.name} - "
            f"{self.addon.name} x {self.quantity}"
        )