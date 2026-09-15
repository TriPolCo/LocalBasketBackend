import uuid

from django.db import models


class FoodCart(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.OneToOneField(
        "accounts.Customer",
        on_delete=models.CASCADE,
        related_name="food_cart",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "food_carts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Food Cart - {self.customer.user.phone_number}"