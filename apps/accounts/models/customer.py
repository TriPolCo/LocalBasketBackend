import uuid
from django.conf import settings
from django.db import models


class Customer(models.Model):
    """
    Customer-specific profile information.

    Authentication and common user information are handled
    by the User model.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="customers/profile/",
        null=True,
        blank=True,
    )

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        null=True,
        blank=True,
    )

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
        db_table = "customers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.phone_number