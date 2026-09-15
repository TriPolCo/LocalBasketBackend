import uuid

from django.db import models


class EmailOTP(models.Model):

    PURPOSE_SIGNUP = "signup"
    PURPOSE_LOGIN = "login"
    PURPOSE_PASSWORD_RESET = "password_reset"

    PURPOSE_CHOICES = [
        (
            PURPOSE_SIGNUP,
            "Signup",
        ),
        (
            PURPOSE_LOGIN,
            "Login",
        ),
        (
            PURPOSE_PASSWORD_RESET,
            "Password Reset",
        ),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        db_index=True,
    )

    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        db_index=True,
    )

    otp_hash = models.CharField(
        max_length=64,
    )

    expires_at = models.DateTimeField(
        db_index=True,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    max_attempts = models.PositiveIntegerField(
        default=5,
    )

    last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_used = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "email_otps"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "email",
                    "purpose",
                    "is_used",
                ],
                name="email_otp_lookup_idx",
            ),
        ]

    def __str__(self):
        return f"{self.email} - {self.purpose}"