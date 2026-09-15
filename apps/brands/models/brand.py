import uuid
from django.db import models

class Brand(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    logo_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
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
        db_table = "brands"
        ordering = ["name"]

    def __str__(self):
        return self.name