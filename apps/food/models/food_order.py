import uuid

from django.db import models


class FoodOrder(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PREPARING = "PREPARING", "Preparing"
        READY = "READY", "Ready"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentMethod(models.TextChoices):
        COD = "COD", "Cash on Delivery"
        ONLINE = "ONLINE", "Online Payment"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

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

    # Customer reference
    customer = models.ForeignKey(
        "accounts.Customer",
        on_delete=models.PROTECT,
        related_name="food_orders",
    )

    # Order status
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    # ==============================
    # PRICING SNAPSHOT
    # ==============================

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    packaging_fee = models.DecimalField(
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
        default=0,
    )

    # ==============================
    # SHIPPING ADDRESS SNAPSHOT
    # ==============================

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

    # ==============================
    # NOTES
    # ==============================

    customer_note = models.TextField(
        blank=True,
        null=True,
    )

    # ==============================
    # TIMESTAMPS
    # ==============================

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
        db_table = "food_orders"

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["customer", "status"],
                name="fo_customer_status_idx",
            ),
            models.Index(
                fields=["customer", "created_at"],
                name="fo_customer_created_idx",
            ),
            models.Index(
                fields=["status", "created_at"],
                name="fo_status_created_idx",
            ),
        ]

    def __str__(self):
        return self.order_number