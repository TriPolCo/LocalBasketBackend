from django.urls import path

from apps.printing.views.printing_service_view import (
    get_printing_services,
    get_printing_pricing,
)

from apps.printing.views.print_order_view import (
    create_print_order,
    get_print_orders,
    get_print_order,
    cancel_print_order,
)

from apps.printing.views.admin_printing_view import (
    admin_get_print_orders,
    admin_get_print_order,
    admin_update_print_order_status,

    admin_get_printing_services,
    admin_create_printing_service,
    admin_update_printing_service,

    admin_get_printing_pricing,
    admin_create_printing_pricing,
    admin_update_printing_pricing,
    admin_delete_printing_pricing,
)


urlpatterns = [

    # =====================================================
    # CUSTOMER
    # =====================================================

    path(
        "services/",
        get_printing_services,
        name="printing-services",
    ),

    path(
        "pricing/",
        get_printing_pricing,
        name="printing-pricing",
    ),

    path(
        "orders/create/",
        create_print_order,
        name="create-print-order",
    ),

    path(
        "orders/",
        get_print_orders,
        name="get-print-orders",
    ),

    path(
        "orders/<uuid:order_id>/",
        get_print_order,
        name="get-print-order",
    ),

    path(
        "orders/<uuid:order_id>/cancel/",
        cancel_print_order,
        name="cancel-print-order",
    ),

    # =====================================================
    # ADMIN ORDERS
    # =====================================================

    path(
        "admin/orders/",
        admin_get_print_orders,
        name="admin-print-orders",
    ),

    path(
        "admin/orders/<uuid:order_id>/",
        admin_get_print_order,
        name="admin-print-order",
    ),

    path(
        "admin/orders/<uuid:order_id>/status/",
        admin_update_print_order_status,
        name="admin-update-print-order-status",
    ),

    # =====================================================
    # ADMIN SERVICES
    # =====================================================

    path(
        "admin/services/",
        admin_get_printing_services,
        name="admin-printing-services",
    ),

    path(
        "admin/services/create/",
        admin_create_printing_service,
        name="admin-create-printing-service",
    ),

    path(
        "admin/services/<uuid:service_id>/update/",
        admin_update_printing_service,
        name="admin-update-printing-service",
    ),

    # =====================================================
    # ADMIN PRICING
    # =====================================================

    path(
        "admin/pricing/",
        admin_get_printing_pricing,
        name="admin-printing-pricing",
    ),

    path(
        "admin/pricing/create/",
        admin_create_printing_pricing,
        name="admin-create-printing-pricing",
    ),

    path(
        "admin/pricing/<uuid:pricing_id>/update/",
        admin_update_printing_pricing,
        name="admin-update-printing-pricing",
    ),

    path(
        "admin/pricing/<uuid:pricing_id>/delete/",
        admin_delete_printing_pricing,
        name="admin-delete-printing-pricing",
    ),
]