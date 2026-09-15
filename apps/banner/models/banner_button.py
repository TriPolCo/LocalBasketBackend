import uuid

from django.db import models

from apps.banner.models.banner import Banner


class BannerButton(models.Model):

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

    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="buttons",
    )

    label = models.CharField(
        max_length=50,
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
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "banner_buttons"
        ordering = ["display_order", "created_at"]

        indexes = [
            models.Index(
                fields=["banner", "is_active"],
                name="banner_btn_active_idx",
            ),
        ]

    def __str__(self):
        return f"{self.banner.title} - {self.label}"