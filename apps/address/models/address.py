import uuid

from django.db import models
from django.db.models import Q


class Address(models.Model):

    class AddressType(models.TextChoices):
        HOME = "HOME", "Home"
        WORK = "WORK", "Work"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        "accounts.Customer",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.HOME,
    )

    full_name = models.CharField(
        max_length=150,
    )

    phone_number = models.CharField(
        max_length=15,
    )

    address_line_1 = models.CharField(
        max_length=255,
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    landmark = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    city = models.CharField(
        max_length=100,
    )

    state = models.CharField(
        max_length=100,
    )

    postal_code = models.CharField(
        max_length=10,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "addresses"
        ordering = ["-is_default", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=Q(is_default=True),
                name="unique_default_address_per_customer",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.city}"