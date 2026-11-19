# apps/orders/models/order.py
import uuid
from decimal import Decimal
from django.db import models


class Order(models.Model):

    # 1. Order Type Choices
    class OrderType(models.TextChoices):
        REGULAR = "REGULAR", "Regular Cart Order"
        IMAGE_LIST = "IMAGE_LIST", "Paper List Upload"
        TEXT_LIST = "TEXT_LIST", "Written Text List"

    class Status(models.TextChoices):
        PENDING_REVIEW = "PENDING_REVIEW", "Pending Review"  # For custom lists before price is set
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

    # 2. Order Type Field
    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.REGULAR,
        db_index=True,
    )

    # 3. Express Order Content Fields
    list_image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Cloudinary URL for uploaded paper list",
    )

    list_text_content = models.TextField(
        null=True,
        blank=True,
        help_text="Customer typed grocery items",
    )

    special_instructions = models.TextField(
        null=True,
        blank=True,
    )

    # 4. Admin-Entered Itemized Bill (for Paper List / Typed List Orders)
    # Example: [{"quantity_label": "1 kg", "product_name": "Potato", "price": 20.0}]
    manual_items = models.JSONField(
    default=list,
    blank=True,
    null=True,
    help_text="Admin-entered itemized bill for IMAGE_LIST / TEXT_LIST orders",
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
        default=Decimal("0.00"),
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
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