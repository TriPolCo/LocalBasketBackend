import uuid

from django.db import models


class PrintingService(models.Model):

    class ServiceType(models.TextChoices):
        PRINT = "PRINT", "Print"
        XEROX = "XEROX", "Xerox"
        SCAN = "SCAN", "Scan"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    service_type = models.CharField(
        max_length=20,
        choices=ServiceType.choices,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "printing_services"
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return self.name