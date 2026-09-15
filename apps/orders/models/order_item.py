import uuid

from django.db import models


class OrderItem(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="items",
    )

    # Original references
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # --------------------------------------------------
    # PRODUCT SNAPSHOT
    # --------------------------------------------------

    product_name = models.CharField(
        max_length=255,
    )

    sku = models.CharField(
        max_length=100,
    )

    # --------------------------------------------------
    # PRICE SNAPSHOT
    # --------------------------------------------------

    quantity = models.PositiveIntegerField()

    mrp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    item_discount = models.DecimalField(
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
        db_table = "order_items"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.order.order_number} - {self.sku}"