import hashlib
import secrets

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from apps.notifications.models.otp import EmailOTP
from apps.notifications.services.email_service import EmailService


class OTPService:

    # ========================================================
    # GENERATE OTP
    # ========================================================

    @staticmethod
    def generate_otp():
        """
        Generate a secure 6-digit OTP.
        """
        return f"{secrets.randbelow(1_000_000):06d}"

    # ========================================================
    # HASH OTP
    # ========================================================

    @staticmethod
    def hash_otp(otp):
        """
        Hash OTP before storing it in database.
        """
        return hashlib.sha256(
            otp.encode("utf-8")
        ).hexdigest()

    # ========================================================
    # NORMALIZE EMAIL
    # ========================================================

    @staticmethod
    def normalize_email(email):
        """
        Normalize email for consistent database lookup.
        """
        return email.strip().lower()

    # ========================================================
    # SEND OTP
    # ========================================================

    @staticmethod
    @transaction.atomic
    def send_otp(
        *,
        email,
        purpose=EmailOTP.PURPOSE_SIGNUP,
    ):

        # ----------------------------------------------------
        # Normalize email
        # ----------------------------------------------------

        email = OTPService.normalize_email(email)

        now = timezone.now()

        # ----------------------------------------------------
        # Find latest active OTP
        # ----------------------------------------------------

        latest_otp = (
            EmailOTP.objects
            .filter(
                email=email,
                purpose=purpose,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        # ----------------------------------------------------
        # Resend protection
        # ----------------------------------------------------

        if latest_otp and latest_otp.last_sent_at:

            elapsed = (
                now - latest_otp.last_sent_at
            ).total_seconds()

            resend_seconds = (
                settings.EMAIL_OTP_RESEND_SECONDS
            )

            if elapsed < resend_seconds:

                remaining = max(
                    1,
                    int(
                        resend_seconds - elapsed
                    ),
                )

                raise ValidationError({
                    "email": (
                        f"Please wait {remaining} "
                        "seconds before requesting "
                        "another OTP."
                    )
                })

        # ----------------------------------------------------
        # Invalidate previous OTPs
        # ----------------------------------------------------

        EmailOTP.objects.filter(
            email=email,
            purpose=purpose,
            is_used=False,
        ).update(
            is_used=True
        )

        # ----------------------------------------------------
        # Generate OTP
        # ----------------------------------------------------

        otp = OTPService.generate_otp()

        otp_hash = OTPService.hash_otp(
            otp
        )

        expires_at = (
            now
            + timedelta(
                minutes=settings.EMAIL_OTP_EXPIRY_MINUTES
            )
        )

        # ----------------------------------------------------
        # Create OTP record
        # ----------------------------------------------------

        otp_record = EmailOTP.objects.create(
            email=email,
            purpose=purpose,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0,
            max_attempts=(
                settings.EMAIL_OTP_MAX_ATTEMPTS
            ),
            last_sent_at=now,
            is_used=False,
        )

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        try:

            EmailService.send_otp_email(
                email=email,
                otp=otp,
                purpose=purpose,
            )

        except Exception as exc:

            # Print the REAL SMTP error in terminal.
            print(
                "\n"
                "==================================================\n"
                "EMAIL OTP ERROR\n"
                "=================================================="
            )

            print(
                f"Email: {email}"
            )

            print(
                f"Error Type: {type(exc).__name__}"
            )

            print(
                f"Error: {str(exc)}"
            )

            print(
                "==================================================\n"
            )

            # Remove OTP record because email failed.
            otp_record.delete()

            # Keep API response user-friendly.
            raise ValidationError({
                "email": (
                    "Unable to send OTP email. "
                    "Please try again later."
                )
            }) from exc

        return otp_record

    # ========================================================
    # VERIFY OTP
    # ========================================================

    @staticmethod
    @transaction.atomic
    def verify_otp(
        *,
        email,
        otp,
        purpose=EmailOTP.PURPOSE_SIGNUP,
    ):

        # ----------------------------------------------------
        # Normalize email
        # ----------------------------------------------------

        email = OTPService.normalize_email(
            email
        )

        # ----------------------------------------------------
        # Normalize OTP
        # ----------------------------------------------------

        otp = otp.strip()

        # ----------------------------------------------------
        # Validate OTP format
        # ----------------------------------------------------

        if not otp.isdigit() or len(otp) != 6:

            raise ValidationError({
                "otp": (
                    "OTP must be a 6-digit number."
                )
            })

        # ----------------------------------------------------
        # Get latest unused OTP
        # ----------------------------------------------------

        otp_record = (
            EmailOTP.objects
            .select_for_update()
            .filter(
                email=email,
                purpose=purpose,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        # ----------------------------------------------------
        # OTP doesn't exist
        # ----------------------------------------------------

        if not otp_record:

            raise ValidationError({
                "otp": (
                    "Invalid or expired OTP."
                )
            })

        # ----------------------------------------------------
        # Check expiry
        # ----------------------------------------------------

        if timezone.now() > otp_record.expires_at:

            otp_record.is_used = True

            otp_record.save(
                update_fields=[
                    "is_used",
                    "updated_at",
                ]
            )

            raise ValidationError({
                "otp": "OTP has expired."
            })

        # ----------------------------------------------------
        # Check maximum attempts
        # ----------------------------------------------------

        if (
            otp_record.attempts
            >= otp_record.max_attempts
        ):

            otp_record.is_used = True

            otp_record.save(
                update_fields=[
                    "is_used",
                    "updated_at",
                ]
            )

            raise ValidationError({
                "otp": (
                    "Maximum OTP verification "
                    "attempts exceeded. "
                    "Please request a new OTP."
                )
            })

        # ----------------------------------------------------
        # Increment attempt
        # ----------------------------------------------------

        otp_record.attempts += 1

        # ----------------------------------------------------
        # Hash incoming OTP
        # ----------------------------------------------------

        incoming_hash = (
            OTPService.hash_otp(otp)
        )

        # ----------------------------------------------------
        # Compare hashes
        # ----------------------------------------------------

        if (
            incoming_hash
            != otp_record.otp_hash
        ):

            otp_record.save(
                update_fields=[
                    "attempts",
                    "updated_at",
                ]
            )

            remaining = (
                otp_record.max_attempts
                - otp_record.attempts
            )

            # If this was the last attempt,
            # invalidate the OTP.
            if remaining <= 0:

                otp_record.is_used = True

                otp_record.save(
                    update_fields=[
                        "attempts",
                        "is_used",
                        "updated_at",
                    ]
                )

                raise ValidationError({
                    "otp": (
                        "Invalid OTP. "
                        "Maximum attempts exceeded. "
                        "Please request a new OTP."
                    )
                })

            raise ValidationError({
                "otp": (
                    "Invalid OTP. "
                    f"{remaining} attempts remaining."
                )
            })

        # ----------------------------------------------------
        # OTP verified successfully
        # ----------------------------------------------------

        otp_record.is_used = True

        otp_record.save(
            update_fields=[
                "attempts",
                "is_used",
                "updated_at",
            ]
        )

        return otp_record