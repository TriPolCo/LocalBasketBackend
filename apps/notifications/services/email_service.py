from django.conf import settings
from django.core.mail import EmailMultiAlternatives


class EmailService:

    # ========================================================
    # SEND OTP EMAIL
    # ========================================================

    @staticmethod
    def send_otp_email(
        *,
        email,
        otp,
        purpose,
    ):
        """
        Send OTP email using Django SMTP configuration.
        """

        # ----------------------------------------------------
        # Validate email configuration
        # ----------------------------------------------------

        if not settings.EMAIL_HOST_USER:
            raise ValueError(
                "EMAIL_HOST_USER is not configured."
            )

        if not settings.EMAIL_HOST_PASSWORD:
            raise ValueError(
                "EMAIL_HOST_PASSWORD is not configured."
            )

        if not settings.DEFAULT_FROM_EMAIL:
            raise ValueError(
                "DEFAULT_FROM_EMAIL is not configured."
            )

        # ----------------------------------------------------
        # Purpose text
        # ----------------------------------------------------

        purpose_text = {
            "signup": (
                "complete your LocalBasket signup"
            ),
            "login": (
                "login to your LocalBasket account"
            ),
            "password_reset": (
                "reset your LocalBasket password"
            ),
        }.get(
            purpose,
            "verify your LocalBasket account",
        )

        # ----------------------------------------------------
        # Subject
        # ----------------------------------------------------

        subject = (
            "Your LocalBasket Verification Code"
        )

        # ----------------------------------------------------
        # Plain text email
        # ----------------------------------------------------

        text_content = f"""
Hello,

Your LocalBasket verification code is:

{otp}

Use this OTP to {purpose_text}.

This OTP will expire in {
    settings.EMAIL_OTP_EXPIRY_MINUTES
} minutes.

For security reasons, do not share this OTP with anyone.

If you did not request this code, you can safely ignore this email.

Regards,
LocalBasket Team
""".strip()

        # ----------------------------------------------------
        # HTML email
        # ----------------------------------------------------

        html_content = f"""
<!DOCTYPE html>

<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        LocalBasket Verification Code
    </title>
</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
        font-family: Arial, Helvetica, sans-serif;
    "
>

    <div
        style="
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 40px;
            box-sizing: border-box;
        "
    >

        <!-- Logo / Brand -->

        <h2
            style="
                margin: 0 0 30px 0;
                text-align: center;
                font-size: 28px;
            "
        >
            LocalBasket
        </h2>


        <!-- Greeting -->

        <p
            style="
                font-size: 16px;
                line-height: 1.6;
                color: #333333;
            "
        >
            Hello,
        </p>


        <p
            style="
                font-size: 16px;
                line-height: 1.6;
                color: #333333;
            "
        >
            Your verification code is:
        </p>


        <!-- OTP -->

        <div
            style="
                text-align: center;
                margin: 30px 0;
            "
        >

            <span
                style="
                    display: inline-block;
                    padding: 16px 30px;
                    background-color: #f3f4f6;
                    border-radius: 10px;
                    font-size: 32px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    color: #111111;
                "
            >
                {otp}
            </span>

        </div>


        <!-- Purpose -->

        <p
            style="
                font-size: 16px;
                line-height: 1.6;
                color: #333333;
            "
        >
            Use this OTP to {purpose_text}.
        </p>


        <!-- Expiry -->

        <p
            style="
                font-size: 16px;
                line-height: 1.6;
                color: #333333;
            "
        >
            This OTP will expire in

            <strong>
                {settings.EMAIL_OTP_EXPIRY_MINUTES} minutes
            </strong>.
        </p>


        <!-- Security -->

        <p
            style="
                font-size: 14px;
                line-height: 1.6;
                color: #666666;
            "
        >
            For security reasons, do not share this OTP with anyone.
        </p>


        <p
            style="
                font-size: 14px;
                line-height: 1.6;
                color: #666666;
            "
        >
            If you did not request this code,
            you can safely ignore this email.
        </p>


        <br>


        <!-- Footer -->

        <p
            style="
                font-size: 15px;
                line-height: 1.6;
                color: #333333;
            "
        >
            Regards,
            <br>

            <strong>
                LocalBasket Team
            </strong>
        </p>

    </div>

</body>

</html>
"""

        # ----------------------------------------------------
        # Create email
        # ----------------------------------------------------

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )

        # ----------------------------------------------------
        # Attach HTML version
        # ----------------------------------------------------

        email_message.attach_alternative(
            html_content,
            "text/html",
        )

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        email_message.send(
            fail_silently=False,
        )

        return True