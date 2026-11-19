# apps/orders/urls.py
from django.urls import path

from apps.orders.views.order_view import (
    place_order,
    upload_list_order,
    type_list_order,
    get_orders,
    get_order,
    cancel_order,
)

from apps.orders.views.admin_order_view import (
    admin_get_all_orders,
    admin_get_order_details,
    admin_update_delivery_fee,
    admin_update_order_status,
    admin_save_express_bill,
)

urlpatterns = [
    # Customer Orders
    path("", get_orders, name="get-orders"),
    path("place/", place_order, name="place-order"),
    path("upload-list/", upload_list_order, name="upload-list-order"),
    path("type-list/", type_list_order, name="type-list-order"),
    path("<uuid:order_id>/", get_order, name="get-order"),
    path("<uuid:order_id>/cancel/", cancel_order, name="cancel-order"),

    # Admin Orders Management
    path("admin/all/", admin_get_all_orders, name="admin-get-all-orders"),
    path("admin/<uuid:order_id>/status/", admin_update_order_status, name="admin-update-order-status"),
    path("admin/<uuid:order_id>/details/", admin_get_order_details, name="admin-get-order-details"),
    path("admin/<uuid:order_id>/delivery-fee/", admin_update_delivery_fee, name="admin-update-delivery-fee"),
    path("admin/<uuid:order_id>/save-bill/", admin_save_express_bill, name="admin-save-express-bill"),
]