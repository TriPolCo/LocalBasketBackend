import uuid

from django.conf import settings
from django.db import models


class Vendor(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
    )

    business_name = models.CharField(
        max_length=150,
    )

    business_email = models.EmailField(
        null=True,
        blank=True,
    )

    business_phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "vendors"
        ordering = ["-created_at"]

    def __str__(self):
        return self.business_name