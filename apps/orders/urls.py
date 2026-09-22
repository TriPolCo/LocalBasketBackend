from django.urls import path

from apps.orders.views.order_view import (
    place_order,
    get_orders,
    get_order,
    cancel_order,
)

from apps.orders.views.admin_order_view import admin_get_all_orders, admin_get_order_details
from apps.orders.views.admin_order_view import admin_update_order_status

urlpatterns = [

    path("",get_orders,name="get-orders",),
    path("place/",place_order,name="place-order",),
    path("<uuid:order_id>/",get_order,name="get-order",),
    path("<uuid:order_id>/cancel/",cancel_order,name="cancel-order",),
    path("admin/all/",admin_get_all_orders,name="admin-get-all-orders",),
    path("admin/<uuid:order_id>/status/",admin_update_order_status,name="admin-update-order-status",),
    path("admin/<uuid:order_id>/details/",admin_get_order_details,name="admin-get-order-details",),
]