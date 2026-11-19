import logging
import ssl
import threading

import certifi
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection

logger = logging.getLogger(__name__)


class EmailNotificationService:
    BRAND_NAME = "DailyDrop"
    PRIMARY_COLOR = "#C9650D"

    @staticmethod
    def _wrap_html(title: str, body_html: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
          <body style="margin:0;padding:24px;background-color:#f8fafc;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
            <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
              <div style="background:{EmailNotificationService.PRIMARY_COLOR};padding:20px 24px;">
                <h1 style="margin:0;color:#ffffff;font-size:20px;letter-spacing:0.3px;">
                  {EmailNotificationService.BRAND_NAME}
                </h1>
              </div>
              <div style="padding:24px;">
                <h2 style="margin:0 0 12px 0;font-size:18px;color:#0f172a;">{title}</h2>
                {body_html}
              </div>
              <div style="background:#f1f5f9;padding:14px 24px;font-size:12px;color:#64748b;text-align:center;">
                This is an automated message from {EmailNotificationService.BRAND_NAME}. Please do not reply.
              </div>
            </div>
          </body>
        </html>
        """

    @staticmethod
    def send_email_sync(
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str,
    ):
        if not to_email:
            return

        connection = get_connection(fail_silently=False)
        connection.ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            connection=connection,
        )
        msg.attach_alternative(html_body, "text/html")

        try:
            msg.send(fail_silently=False)
        except Exception as exc:
            print("❌ SMTP EMAIL ERROR:", repr(exc))
            raise

    @staticmethod
    def send_email_async(
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str,
    ):
        if not to_email or not settings.EMAIL_HOST_USER:
            return

        def _worker():
            try:
                EmailNotificationService.send_email_sync(
                    to_email=to_email,
                    subject=subject,
                    text_body=text_body,
                    html_body=html_body,
                )
            except Exception as exc:
                logger.warning("Email send failed to %s: %s", to_email, exc)

        threading.Thread(target=_worker, daemon=True).start()

    # ==========================================================
    # 1. FORGOT PASSWORD OTP EMAIL
    # ==========================================================
    @classmethod
    def send_forgot_password_otp(
        cls, email: str, otp: str, first_name: str = ""
    ):
        name = first_name or "there"
        subject = f"{otp} is your {cls.BRAND_NAME} password reset code"
        text_body = (
            f"Hi {name},\n\n"
            f"Use this 6-digit code to reset your {cls.BRAND_NAME} password: {otp}\n"
            f"This code expires in 10 minutes.\n\n"
            f"If you did not request this, you can safely ignore this email."
        )
        body_html = f"""
        <p style="font-size:14px;line-height:22px;color:#334155;">Hi <b>{name}</b>,</p>
        <p style="font-size:14px;line-height:22px;color:#334155;">
          Use the 6-digit verification code below to reset your password:
        </p>
        <div style="margin:20px 0;padding:16px;background:#ecfdf5;border:1px dashed #047857;border-radius:10px;text-align:center;">
          <span style="font-size:32px;font-weight:800;letter-spacing:8px;color:#047857;">{otp}</span>
        </div>
        <p style="font-size:13px;color:#64748b;">
          This code is valid for <b>10 minutes</b>. Do not share it with anyone.
        </p>
        """
        cls.send_email_sync(
            to_email=email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html("Reset Your Password", body_html),
        )

    # ==========================================================
    # 2. PASSWORD RESET CONFIRMATION EMAIL
    # ==========================================================
    @classmethod
    def send_password_changed_email(cls, email: str, first_name: str = ""):
        name = first_name or "there"
        subject = f"Your {cls.BRAND_NAME} password was changed"
        text_body = (
            f"Hi {name},\n\n"
            f"Your {cls.BRAND_NAME} password has been successfully updated.\n"
            f"If you did not make this change, please contact support immediately."
        )
        body_html = f"""
        <p style="font-size:14px;line-height:22px;color:#334155;">Hi <b>{name}</b>,</p>
        <p style="font-size:14px;line-height:22px;color:#334155;">
          Your account password was changed successfully. You can now log in with your new password.
        </p>
        <p style="font-size:13px;color:#64748b;">
          If you didn't do this, please reset your password again or contact support immediately.
        </p>
        """
        cls.send_email_async(
            to_email=email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html("Password Updated", body_html),
        )

    # ==========================================================
    # 3. CUSTOMER: ORDER PLACED EMAIL
    # ==========================================================
    @classmethod
    def send_order_placed_email(cls, order):
        customer_obj = getattr(order, "customer", None)
        user = getattr(customer_obj, "user", None) or customer_obj
        to_email = getattr(user, "email", None)
        if not to_email:
            return

        name = getattr(order, "shipping_full_name", None) or getattr(
            user, "first_name", "Customer"
        )
        order_number = getattr(order, "order_number", str(order.id)[:8])
        total_amount = float(getattr(order, "total_amount", 0) or 0)
        order_type = getattr(order, "order_type", "REGULAR")

        total_text = (
            f"Rs. {total_amount:,.2f}"
            if total_amount > 0
            else "Pending Admin Bill Review"
        )

        subject = f"Order Confirmed: #{order_number}"
        text_body = (
            f"Hi {name},\n\n"
            f"Thank you for your order #{order_number} on {cls.BRAND_NAME}!\n"
            f"Total: {total_text}\n"
            f"We will notify you as soon as your order is out for delivery."
        )
        body_html = f"""
        <p style="font-size:14px;color:#334155;">Hi <b>{name}</b>,</p>
        <p style="font-size:14px;color:#334155;">
          We've received your order <b>#{order_number}</b> ({order_type}).
        </p>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px;margin:16px 0;">
          <p style="margin:4px 0;font-size:13px;"><b>Order ID:</b> #{order_number}</p>
          <p style="margin:4px 0;font-size:13px;"><b>Total:</b> {total_text}</p>
          <p style="margin:4px 0;font-size:13px;"><b>Status:</b> {order.status}</p>
        </div>
        <p style="font-size:13px;color:#64748b;">We'll keep you updated as your order moves to delivery.</p>
        """
        cls.send_email_async(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html("Order Confirmed!", body_html),
        )

    # ==========================================================
    # 4. CUSTOMER: EXPRESS BILL READY EMAIL
    # ==========================================================
    @classmethod
    def send_express_bill_ready_email(cls, order):
        customer_obj = getattr(order, "customer", None)
        user = getattr(customer_obj, "user", None) or customer_obj
        to_email = getattr(user, "email", None)
        if not to_email:
            return

        name = getattr(order, "shipping_full_name", None) or getattr(
            user, "first_name", "Customer"
        )
        order_number = getattr(order, "order_number", str(order.id)[:8])
        total_amount = float(getattr(order, "total_amount", 0) or 0)
        manual_items = getattr(order, "manual_items", None) or []

        rows_html = "".join(
            f"<tr>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #e2e8f0;font-size:13px;'>{it.get('name', '')}</td>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #e2e8f0;font-size:13px;'>{it.get('quantity', '')}</td>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #e2e8f0;font-size:13px;text-align:right;'>Rs. {float(it.get('price', 0)):,.2f}</td>"
            f"</tr>"
            for it in manual_items
        )

        subject = f"Bill Ready for Order #{order_number} (Rs. {total_amount:,.2f})"
        text_body = (
            f"Hi {name},\n\n"
            f"Your itemized bill for order #{order_number} is ready.\n"
            f"Grand Total: Rs. {total_amount:,.2f}\n"
            f"Open the {cls.BRAND_NAME} app to view the full receipt."
        )
        body_html = f"""
        <p style="font-size:14px;color:#334155;">Hi <b>{name}</b>,</p>
        <p style="font-size:14px;color:#334155;">
          Your grocery list bill for order <b>#{order_number}</b> has been prepared:
        </p>
        <table style="width:100%;border-collapse:collapse;margin:14px 0;">
          <thead>
            <tr style="background:#f1f5f9;">
              <th style="padding:8px;text-align:left;font-size:12px;">Item</th>
              <th style="padding:8px;text-align:left;font-size:12px;">Qty</th>
              <th style="padding:8px;text-align:right;font-size:12px;">Amount</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        <p style="font-size:16px;font-weight:700;text-align:right;color:#047857;">
          Grand Total: Rs. {total_amount:,.2f}
        </p>
        """
        cls.send_email_async(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html("Your Itemized Bill is Ready", body_html),
        )

    # ==========================================================
    # 5. CUSTOMER: DELIVERY STATUS UPDATE (OUT FOR DELIVERY / DELIVERED)
    # ==========================================================
    @classmethod
    def send_delivery_status_email(cls, order, title: str, message: str):
        if not order:
            return
        customer_obj = getattr(order, "customer", None)
        user = getattr(customer_obj, "user", None) or customer_obj
        to_email = getattr(user, "email", None)
        if not to_email:
            return

        name = getattr(order, "shipping_full_name", None) or getattr(
            user, "first_name", "Customer"
        )
        order_number = getattr(order, "order_number", str(order.id)[:8])
        subject = f"{title} — Order #{order_number}"
        text_body = f"Hi {name},\n\nOrder #{order_number}: {message}"
        body_html = f"""
        <p style="font-size:14px;color:#334155;">Hi <b>{name}</b>,</p>
        <p style="font-size:14px;line-height:22px;color:#334155;">{message}</p>
        <p style="font-size:13px;color:#64748b;"><b>Order ID:</b> #{order_number}</p>
        """
        cls.send_email_async(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html(title, body_html),
        )

    # ==========================================================
    # 6. DELIVERY PARTNER: NEW ASSIGNMENT EMAIL
    # ==========================================================
    @classmethod
    def send_partner_assigned_email(cls, assignment):
        partner_user = getattr(assignment.delivery_partner, "user", None)
        to_email = getattr(partner_user, "email", None)
        if not to_email:
            return

        target = assignment.order or assignment.food_order
        order_number = getattr(target, "order_number", str(assignment.id)[:8])
        customer_name = getattr(target, "shipping_full_name", "Customer")
        total = float(getattr(target, "total_amount", 0) or 0)

        subject = f"New Delivery Assigned: #{order_number}"
        text_body = (
            f"Hi {partner_user.first_name or 'Partner'},\n\n"
            f"Order #{order_number} for {customer_name} (Rs. {total:,.2f}) has been assigned to you.\n"
            f"Open the {cls.BRAND_NAME} Delivery App to accept and start delivery."
        )
        body_html = f"""
        <p style="font-size:14px;color:#334155;">Hi <b>{partner_user.first_name or 'Partner'}</b>,</p>
        <p style="font-size:14px;color:#334155;">A new delivery has been assigned to you:</p>
        <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:14px;margin:16px 0;">
          <p style="margin:4px 0;font-size:13px;"><b>Order:</b> #{order_number}</p>
          <p style="margin:4px 0;font-size:13px;"><b>Customer:</b> {customer_name}</p>
          <p style="margin:4px 0;font-size:13px;"><b>Order Total:</b> Rs. {total:,.2f}</p>
        </div>
        <p style="font-size:13px;color:#64748b;">Open your Delivery Partner app to accept and deliver.</p>
        """
        cls.send_email_async(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html("New Delivery Assigned", body_html),
        )



            # ==========================================================
    # 7. SIGNUP EMAIL VERIFICATION OTP
    # ==========================================================
    @classmethod
    def send_signup_verification_otp(cls, to_email: str, otp: str):
        if not to_email:
            return

        subject = f"Your DailyDrop Verification Code: {otp}"
        text_body = (
            f"Welcome to {cls.BRAND_NAME}!\n\n"
            f"Your email verification code is: {otp}\n\n"
            f"This code is valid for 10 minutes. Please enter it to complete your registration.\n\n"
            f"If you did not request this, please ignore this email."
        )

        body_html = f"""
        <p style="font-size:15px;color:#334155;margin:0 0 16px;">Welcome to <b>{cls.BRAND_NAME}</b>!</p>
        <p style="font-size:14px;color:#64748b;margin:0 0 20px;">Use the verification code below to verify your email address and activate your account:</p>
        
        <div style="background:#f0fdf4;border:2px dashed #059669;border-radius:12px;padding:20px;text-align:center;margin:24px 0;">
            <span style="font-size:32px;font-weight:800;letter-spacing:8px;color:#047857;font-family:monospace;">{otp}</span>
        </div>
        
        <p style="font-size:12px;color:#94a3b8;margin:20px 0 0;">This code will expire in <b>10 minutes</b>. Never share this code with anyone.</p>
        """

        cls.send_email_async(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=cls._wrap_html("Verify Your Email Address", body_html),
        )