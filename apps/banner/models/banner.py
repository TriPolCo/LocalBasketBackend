import uuid

from django.db import models
from django.utils import timezone


class Banner(models.Model):

    class Section(models.TextChoices):
        HOME = "HOME", "Home"
        GROCERY = "GROCERY", "Grocery"
        FOOD = "FOOD", "Food"
        PRINTING = "PRINTING", "Printing"

    class NavigationType(models.TextChoices):
        NONE = "NONE", "None"
        CATEGORY = "CATEGORY", "Category"
        SUBCATEGORY = "SUBCATEGORY", "Subcategory"
        PRODUCT = "PRODUCT", "Product"
        FOOD_CATEGORY = "FOOD_CATEGORY", "Food Category"
        FOOD_ITEM = "FOOD_ITEM", "Food Item"
        URL = "URL", "External URL"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    title = models.CharField(
        max_length=200,
    )

    subtitle = models.CharField(
        max_length=300,
        blank=True,
        null=True,
    )

    # Desktop / large screen image
    image_url = models.URLField(
        max_length=1000,
    )

    image_public_id = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    # Optional mobile-specific image
    mobile_image_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
    )

    mobile_image_public_id = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    section = models.CharField(
        max_length=30,
        choices=Section.choices,
        default=Section.HOME,
        db_index=True,
    )

    navigation_type = models.CharField(
        max_length=30,
        choices=NavigationType.choices,
        default=NavigationType.NONE,
    )

    navigation_id = models.UUIDField(
        null=True,
        blank=True,
    )

    navigation_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    start_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    end_at = models.DateTimeField(
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
        db_table = "banners"
        ordering = ["display_order", "-created_at"]

        indexes = [
            models.Index(
                fields=["section", "is_active"],
                name="banner_section_active_idx",
            ),
            models.Index(
                fields=["start_at", "end_at"],
                name="banner_schedule_idx",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def is_currently_active(self):
        now = timezone.now()

        if not self.is_active:
            return False

        if self.start_at and now < self.start_at:
            return False

        if self.end_at and now > self.end_at:
            return False

        return True