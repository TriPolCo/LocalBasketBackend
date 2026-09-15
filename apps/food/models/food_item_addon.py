import uuid

from django.db import models


class FoodItemAddon(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    food_item = models.ForeignKey(
        "food.FoodItem",
        on_delete=models.CASCADE,
        related_name="addons",
    )

    name = models.CharField(
        max_length=150,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    is_required = models.BooleanField(
        default=False,
    )

    max_quantity = models.PositiveIntegerField(
        default=1,
    )

    is_available = models.BooleanField(
        default=True,
        db_index=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "food_item_addons"
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return self.name