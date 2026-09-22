import uuid

from django.db import models


class Invoice(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="invoice",
    )

    qr_token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "invoices"
        ordering = ["-generated_at"]

    def __str__(self):
        return self.invoice_number