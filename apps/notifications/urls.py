from django.urls import path
from apps.notifications.views.otp_view import (send_email_otp,verify_email_otp,)

urlpatterns = [
    path("email-otp/send/",send_email_otp,name="send-email-otp",),
    path("email-otp/verify/",verify_email_otp,name="verify-email-otp",),
]