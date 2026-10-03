import uuid

from django.db import models


class DeliveryAssignment(models.Model):

    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        ACCEPTED = "ACCEPTED", "Accepted"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        ONLINE = "ONLINE", "Online"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ==========================================================
    # NORMAL ORDER
    # ==========================================================

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="delivery_assignment",
        null=True,
        blank=True,
    )

    # ==========================================================
    # FOOD ORDER
    # ==========================================================

    food_order = models.OneToOneField(
        "food.FoodOrder",
        on_delete=models.CASCADE,
        related_name="delivery_assignment",
        null=True,
        blank=True,
    )

    # ==========================================================
    # DELIVERY PARTNER
    # ==========================================================

    delivery_partner = models.ForeignKey(
        "accounts.DeliveryPartner",
        on_delete=models.PROTECT,
        related_name="delivery_assignments",
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED,
    )

    # ==========================================================
    # DELIVERY PROOF
    # ==========================================================

    delivery_image_url = models.URLField(
        max_length=1000,
        null=True,
        blank=True,
    )

    delivery_image_public_id = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )

    # ==========================================================
    # PAYMENT
    # ==========================================================

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True,
    )

    payment_confirmed = models.BooleanField(
        default=False,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "delivery_assignments"
        ordering = ["-assigned_at"]

    def __str__(self):
        target = self.food_order_id or self.order_id

        return (
            f"{target} - "
            f"{self.delivery_partner_id} - "
            f"{self.status}"
        )