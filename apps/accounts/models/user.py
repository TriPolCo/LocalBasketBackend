import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.accounts.managers.user_manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        VENDOR = "VENDOR", "Vendor"
        DELIVERY_PARTNER = "DELIVERY_PARTNER", "Delivery Partner"
        ADMIN = "ADMIN", "Admin"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True
    )

    first_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )

    profile_image_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
    )

    profile_image_public_id = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    phone_verified = models.BooleanField(default=False)

    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone_number