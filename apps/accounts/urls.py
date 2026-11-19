# apps/accounts/urls.py
from django.urls import path

from apps.accounts.views.admin_account_view import (
    superuser_update_password,
    superuser_update_email,
    superuser_update_phone,
    get_superuser_profile,
)
from apps.accounts.views.delivery_partner_admin_view import (
    get_delivery_partners,
    create_delivery_partner,
    get_delivery_partner,
    update_delivery_partner,
    delete_delivery_partner,
)
from apps.accounts.views.delivery_partner_view import (
    delivery_partner_login,
    get_delivery_partner_profile,
    update_delivery_partner_profile,
    change_delivery_partner_password,
    update_delivery_partner_availability,
)
from apps.accounts.views.auth_views import (
    register,
    login,
    send_otp,
    verify_otp,
    update_profile_image,
    get_current_user,
    send_signup_email_otp,
    verify_signup_email_otp,
    store_call_to_order_phone,
)

from apps.accounts.views.password_reset_views import (
    forgot_password_send_otp,
    forgot_password_verify_otp,
    forgot_password_reset,
)
from apps.accounts.views.admin_auth_views import admin_login_view
from apps.accounts.views.admin_user_view import admin_get_all_users


urlpatterns = [
    # ========================================================
    # USER & CUSTOMER AUTH (OTP & PASSWORD)
    # ========================================================
    path("user/send-otp/", send_otp, name="send-otp"),
    path("user/verify-otp/", verify_otp, name="verify-otp"),
    path("user/register/", register, name="register"),

    # 🆕 SIGNUP EMAIL OTP VERIFICATION
    path("user/register/send-email-otp/", send_signup_email_otp, name="signup-send-email-otp"),
    path("user/register/verify-email-otp/", verify_signup_email_otp, name="signup-verify-email-otp"),
    # Direct aliases for convenience
    path("register/send-email-otp/", send_signup_email_otp, name="signup-send-email-otp-alias"),
    path("register/verify-email-otp/", verify_signup_email_otp, name="signup-verify-email-otp-alias"),

    path("user/login/", login, name="user-login"),
    path("user/profile/image/", update_profile_image, name="update-profile-image"),
    path("user/profile/", get_current_user, name="get-current-user"),

    # ========================================================
    # 🆕 STORE / CALL TO ORDER PHONE (PUBLIC GET & ADMIN UPDATE)
    # ========================================================
    path("call-to-order/", store_call_to_order_phone, name="call-to-order-phone"),
    path("user/call-to-order/", store_call_to_order_phone, name="call-to-order-phone-alias"),
    path("store-phone/", store_call_to_order_phone, name="store-phone"),
    path("admin/store-phone/update/", store_call_to_order_phone, name="admin-update-store-phone"),
    path("admin/call-to-order/", store_call_to_order_phone, name="admin-call-to-order"),

    # ========================================================
    # ADMIN
    # ========================================================
    path("admin/login/", admin_login_view, name="admin-login"),
    path("admin/users/", admin_get_all_users, name="admin-get-all-users"),

    # ========================================================
    # SUPERUSER
    # ========================================================
    path("superuser/profile/", get_superuser_profile, name="superuser-profile"),
    path("superuser/update-password/", superuser_update_password, name="superuser-update-password"),
    path("superuser/update-email/", superuser_update_email, name="superuser-update-email"),
    path("superuser/update-phone/", superuser_update_phone, name="superuser-update-phone"),

    # ========================================================
    # ADMIN - DELIVERY PARTNERS
    # ========================================================
    path("admin/delivery-partners/", get_delivery_partners, name="admin-delivery-partners"),
    path("admin/delivery-partners/create/", create_delivery_partner, name="admin-create-delivery-partner"),
    path("admin/delivery-partners/<uuid:delivery_partner_id>/", get_delivery_partner, name="admin-delivery-partner-detail"),
    path("admin/delivery-partners/<uuid:delivery_partner_id>/update/", update_delivery_partner, name="admin-update-delivery-partner"),
    path("admin/delivery-partners/<uuid:delivery_partner_id>/delete/", delete_delivery_partner, name="admin-delete-delivery-partner"),

    # ========================================================
    # DELIVERY PARTNER AUTH
    # ========================================================
    path("delivery-partner/login/", delivery_partner_login, name="delivery-partner-login"),
    path("delivery-partner/profile/", get_delivery_partner_profile, name="delivery-partner-profile"),
    path("delivery-partner/profile/update/", update_delivery_partner_profile, name="delivery-partner-profile-update"),
    path("delivery-partner/change-password/", change_delivery_partner_password, name="delivery-partner-change-password"),
    path("delivery-partner/availability/", update_delivery_partner_availability, name="delivery-partner-availability"),

    # ========================================================
    # FORGOT PASSWORD (EMAIL OTP)
    # ========================================================
    path("user/forgot-password/send-otp/", forgot_password_send_otp, name="forgot-password-send-otp"),
    path("user/forgot-password/verify-otp/", forgot_password_verify_otp, name="forgot-password-verify-otp"),
    path("user/forgot-password/reset-password/", forgot_password_reset, name="forgot-password-reset"),
]