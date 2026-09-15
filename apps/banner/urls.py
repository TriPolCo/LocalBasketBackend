from django.urls import path

from apps.banner.views.banner_view import (
    create_banner,
    get_banners,
)

urlpatterns = [
    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/create/",
        create_banner,
        name="admin-create-banner",
    ),

    # ========================================================
    # APP
    # ========================================================

    path(
        "",
        get_banners,
        name="get-banners",
    ),
]