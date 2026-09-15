import uuid
from django.db import models


class Cart(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.OneToOneField(
        "accounts.Customer",
        on_delete=models.CASCADE,
        related_name="cart",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "carts"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Cart - {self.customer.user.phone_number}"