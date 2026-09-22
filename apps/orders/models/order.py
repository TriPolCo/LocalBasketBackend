import uuid

from django.db import models


class Order(models.Model):

    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
    )

    customer = models.ForeignKey(
        "accounts.Customer",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    # Original address reference
    shipping_address = models.ForeignKey(
        "address.Address",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )

    # --------------------------------------------------
    # ADDRESS SNAPSHOT
    # --------------------------------------------------

    shipping_full_name = models.CharField(
        max_length=150,
    )

    shipping_phone_number = models.CharField(
        max_length=15,
    )

    shipping_address_line_1 = models.CharField(
        max_length=255,
    )

    shipping_address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    shipping_landmark = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    shipping_city = models.CharField(
        max_length=100,
    )

    shipping_state = models.CharField(
        max_length=100,
    )

    shipping_postal_code = models.CharField(
        max_length=10,
    )

    shipping_country = models.CharField(
        max_length=100,
        default="India",
    )

    # --------------------------------------------------
    # PAYMENT
    # --------------------------------------------------

    # COD only for now
    payment_method = models.CharField(
        max_length=20,
        default="COD",
        editable=False,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    # --------------------------------------------------
    # AMOUNTS
    # --------------------------------------------------

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    # --------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
        db_index=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["customer", "status"],
                name="order_customer_status_idx",
            ),
            models.Index(
                fields=["customer", "created_at"],
                name="order_customer_created_idx",
            ),
        ]

    def __str__(self):
        return self.order_number