import uuid

from django.conf import settings
from django.db import models


class AdminProfile(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile",
    )

    profile_image = models.ImageField(
        upload_to="admins/profile/",
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
        db_table = "admin_profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.phone_number