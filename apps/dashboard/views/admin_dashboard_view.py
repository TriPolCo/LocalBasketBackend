from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.dashboard.services.admin_dashboard_service import (
    AdminDashboardService,
)

from apps.dashboard.serializers.admin_dashboard_serializer import (
    DashboardSummarySerializer,
    OrdersTrendSerializer,
    OrdersStatusSerializer,
    RecentOrderSerializer,
    UserRegistrationSerializer,
)


# =========================================================
# MAIN DASHBOARD
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):

    period = request.query_params.get(
        "period",
        "30d",
    )

    start_date = request.query_params.get(
        "start_date"
    )

    end_date = request.query_params.get(
        "end_date"
    )

    data = AdminDashboardService.get_dashboard(
        period=period,
        start_date=start_date,
        end_date=end_date,
    )

    summary_serializer = DashboardSummarySerializer(
        data["summary"]
    )

    trend_serializer = OrdersTrendSerializer(
        data["orders_trend"],
        many=True,
    )

    status_serializer = OrdersStatusSerializer(
        data["orders_by_status"],
        many=True,
    )

    recent_orders_serializer = RecentOrderSerializer(
        [
            {
                "id": order.id,
                "order_number": order.order_number,
                "customer": {
                    "id": order.customer.id,
                    "name": (
                        f"{order.customer.user.first_name} "
                        f"{order.customer.user.last_name}"
                    ).strip(),
                    "phone_number": (
                        order.customer.user.phone_number
                    ),
                },
                "created_at": order.created_at,
                "status": order.status,
                "total_amount": order.total_amount,
            }
            for order in data["recent_orders"]
        ],
        many=True,
    )

    registration_serializer = UserRegistrationSerializer(
        data["new_user_registrations"],
        many=True,
    )

    return Response({
        "success": True,
        "message": "Dashboard data fetched successfully.",
        "data": {
            "period": {
                "start_date": data["period"]["start_date"],
                "end_date": data["period"]["end_date"],
            },
            "summary": summary_serializer.data,
            "orders_trend": trend_serializer.data,
            "orders_by_status": status_serializer.data,
            "recent_orders": recent_orders_serializer.data,
            "new_user_registrations": (
                registration_serializer.data
            ),
        },
    })


# =========================================================
# ORDERS TREND
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_orders_trend(request):

    period = request.query_params.get(
        "period",
        "30d",
    )

    start_date = request.query_params.get(
        "start_date"
    )

    end_date = request.query_params.get(
        "end_date"
    )

    start_date, end_date = (
        AdminDashboardService.get_date_range(
            period=period,
            start_date=start_date,
            end_date=end_date,
        )
    )

    data = AdminDashboardService.get_orders_trend(
        start_date=start_date,
        end_date=end_date,
    )

    serializer = OrdersTrendSerializer(
        data,
        many=True,
    )

    return Response({
        "success": True,
        "message": "Orders trend fetched successfully.",
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "results": serializer.data,
        },
    })


# =========================================================
# ORDERS STATUS
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_orders_status(request):

    period = request.query_params.get(
        "period",
        "30d",
    )

    start_date = request.query_params.get(
        "start_date"
    )

    end_date = request.query_params.get(
        "end_date"
    )

    start_date, end_date = (
        AdminDashboardService.get_date_range(
            period=period,
            start_date=start_date,
            end_date=end_date,
        )
    )

    data = AdminDashboardService.get_orders_by_status(
        start_date=start_date,
        end_date=end_date,
    )

    serializer = OrdersStatusSerializer(
        data,
        many=True,
    )

    return Response({
        "success": True,
        "message": "Order status data fetched successfully.",
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "results": serializer.data,
        },
    })


# =========================================================
# RECENT ORDERS
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_recent_orders(request):

    limit = request.query_params.get(
        "limit",
        "5",
    )

    try:
        limit = int(limit)

    except ValueError:
        limit = 5

    limit = max(
        1,
        min(limit, 20),
    )

    orders = AdminDashboardService.get_recent_orders(
        limit=limit,
    )

    serializer = RecentOrderSerializer(
        [
            {
                "id": order.id,
                "order_number": order.order_number,
                "customer": {
                    "id": order.customer.id,
                    "name": (
                        f"{order.customer.user.first_name} "
                        f"{order.customer.user.last_name}"
                    ).strip(),
                    "phone_number": (
                        order.customer.user.phone_number
                    ),
                },
                "created_at": order.created_at,
                "status": order.status,
                "total_amount": order.total_amount,
            }
            for order in orders
        ],
        many=True,
    )

    return Response({
        "success": True,
        "message": "Recent orders fetched successfully.",
        "data": serializer.data,
    })


# =========================================================
# USER REGISTRATIONS
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_user_registrations(request):

    period = request.query_params.get(
        "period",
        "30d",
    )

    start_date = request.query_params.get(
        "start_date"
    )

    end_date = request.query_params.get(
        "end_date"
    )

    start_date, end_date = (
        AdminDashboardService.get_date_range(
            period=period,
            start_date=start_date,
            end_date=end_date,
        )
    )

    data = AdminDashboardService.get_user_registrations(
        start_date=start_date,
        end_date=end_date,
    )

    serializer = UserRegistrationSerializer(
        data,
        many=True,
    )

    return Response({
        "success": True,
        "message": "User registration data fetched successfully.",
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "results": serializer.data,
        },
    })