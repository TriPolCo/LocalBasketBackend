from django.urls import path
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
path(
        "admin/users/",
        admin_get_all_users,
        name="admin-get-all-users",
    ),
]