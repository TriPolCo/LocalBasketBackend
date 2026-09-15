import uuid

from django.db import models


class FoodItem(models.Model):

    class FoodType(models.TextChoices):
        VEG = "VEG", "Vegetarian"
        NON_VEG = "NON_VEG", "Non Vegetarian"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    category = models.ForeignKey(
        "food.MenuCategory",
        on_delete=models.PROTECT,
        related_name="food_items",
    )

    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    image_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
    )

    cloudinary_public_id = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    food_type = models.CharField(
        max_length=20,
        choices=FoodType.choices,
        db_index=True,
    )

    is_available = models.BooleanField(
        default=True,
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    is_bestseller = models.BooleanField(
        default=False,
    )

    is_recommended = models.BooleanField(
        default=False,
    )

    preparation_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Preparation time in minutes",
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
        db_table = "food_items"
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return self.name