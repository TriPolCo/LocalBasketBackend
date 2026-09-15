import uuid

from django.db import models


class PrintPricing(models.Model):

    class ColorType(models.TextChoices):
        BLACK_WHITE = "BLACK_WHITE", "Black & White"
        COLOR = "COLOR", "Color"

    class PaperSize(models.TextChoices):
        A4 = "A4", "A4"
        A3 = "A3", "A3"
        A5 = "A5", "A5"

    class PrintSide(models.TextChoices):
        SINGLE = "SINGLE", "Single Side"
        DOUBLE = "DOUBLE", "Double Side"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    service = models.ForeignKey(
        "printing.PrintingService",
        on_delete=models.PROTECT,
        related_name="pricing",
    )

    color_type = models.CharField(
        max_length=20,
        choices=ColorType.choices,
        default=ColorType.BLACK_WHITE,
    )

    paper_size = models.CharField(
        max_length=10,
        choices=PaperSize.choices,
        default=PaperSize.A4,
    )

    print_side = models.CharField(
        max_length=10,
        choices=PrintSide.choices,
        default=PrintSide.SINGLE,
    )

    price_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    minimum_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "print_pricing"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "service",
                    "color_type",
                    "paper_size",
                    "print_side",
                ],
                name="unique_print_pricing_configuration",
            ),
        ]

        ordering = [
            "service",
            "paper_size",
            "color_type",
            "print_side",
        ]

    def __str__(self):
        return (
            f"{self.service.name} - "
            f"{self.paper_size} - "
            f"{self.color_type} - "
            f"{self.print_side}"
        )