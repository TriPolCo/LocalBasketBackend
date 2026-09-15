import uuid

from django.db import models


class PrintDocument(models.Model):

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

    print_order = models.ForeignKey(
        "printing.PrintOrder",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    service = models.ForeignKey(
        "printing.PrintingService",
        on_delete=models.PROTECT,
        related_name="documents",
    )

    file_name = models.CharField(
        max_length=255,
    )

    file_url = models.URLField(
        max_length=1000,
    )

    cloudinary_public_id = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    file_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    page_count = models.PositiveIntegerField(
        default=1,
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

    copies = models.PositiveIntegerField(
        default=1,
    )

    page_start = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    page_end = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    price_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
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
        db_table = "print_documents"

        ordering = [
            "display_order",
            "created_at",
        ]

    def __str__(self):
        return self.file_name