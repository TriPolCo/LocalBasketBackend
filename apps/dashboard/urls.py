from django.urls import path

from apps.dashboard.views.admin_dashboard_view import admin_dashboard, admin_orders_trend, admin_orders_status, \
    admin_recent_orders, admin_user_registrations

urlpatterns = [

    # Complete dashboard
    path(
        "",
        admin_dashboard,
        name="admin-dashboard",
    ),

    # Orders trend
    path(
        "orders-trend/",
        admin_orders_trend,
        name="admin-orders-trend",
    ),

    # Orders by status
    path(
        "orders-status/",
        admin_orders_status,
        name="admin-orders-status",
    ),

    # Recent orders
    path(
        "recent-orders/",
        admin_recent_orders,
        name="admin-recent-orders",
    ),

    # User registrations
    path(
        "user-registrations/",
        admin_user_registrations,
        name="admin-user-registrations",
    ),
]