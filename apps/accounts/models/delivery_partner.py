import uuid

from django.conf import settings
from django.db import models


class DeliveryPartner(models.Model):

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delivery_partner_profile",
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="delivery_partners/profile/",
        null=True,
        blank=True,
    )

    is_available = models.BooleanField(
        default=False,
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
    )

    total_deliveries = models.PositiveIntegerField(
        default=0,
    )

    completed_deliveries = models.PositiveIntegerField(
        default=0,
    )

    cancelled_deliveries = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "delivery_partners"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.phone_number