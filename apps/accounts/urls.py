from django.urls import path

from apps.accounts.views.delivery_partner_admin_view import get_delivery_partners, create_delivery_partner, \
    get_delivery_partner, update_delivery_partner, delete_delivery_partner
from apps.accounts.views.delivery_partner_view import delivery_partner_login, get_delivery_partner_profile, \
    update_delivery_partner_profile, change_delivery_partner_password, update_delivery_partner_availability
from apps.accounts.views.auth_views import register,login,update_profile_image,get_current_user
from apps.accounts.views.admin_auth_views import admin_login_view
from apps.accounts.views.admin_user_view import admin_get_all_users


urlpatterns = [
    path("user/register/",register,name="register",),
    path("user/login/",login,name="user-login",),
    path("user/profile/image/",update_profile_image,name="update-profile-image",),
    path("user/profile/",get_current_user,name="get-current-user",),



    #Admin
    path("admin/login/",admin_login_view,name="admin-login",),
    path("admin/users/",admin_get_all_users,name="admin-get-all-users",),


    # ADMIN - DELIVERY PARTNERS

    path("admin/delivery-partners/",get_delivery_partners,name="admin-delivery-partners",),
    path("admin/delivery-partners/create/",create_delivery_partner,name="admin-create-delivery-partner",),
    path("admin/delivery-partners/<uuid:delivery_partner_id>/",get_delivery_partner,name="admin-delivery-partner-detail",),
    path("admin/delivery-partners/<uuid:delivery_partner_id>/update/",update_delivery_partner,name="admin-update-delivery-partner",),
    path("admin/delivery-partners/<uuid:delivery_partner_id>/delete/",delete_delivery_partner,name="admin-delete-delivery-partner",),

    # DELIVERY PARTNER AUTH
    path("delivery-partner/login/",delivery_partner_login,name="delivery-partner-login",),
    path("delivery-partner/profile/",get_delivery_partner_profile,name="delivery-partner-profile",),
    path("delivery-partner/profile/update/",update_delivery_partner_profile, name="delivery-partner-profile-update",),
    path("delivery-partner/change-password/",change_delivery_partner_password, name="delivery-partner-change-password",),
    path("delivery-partner/availability/",update_delivery_partner_availability,name="delivery-partner-availability",),
]