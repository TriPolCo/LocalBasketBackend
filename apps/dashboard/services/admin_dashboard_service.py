import logging
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.orders.models.order import Order


logger = logging.getLogger(__name__)

User = get_user_model()


class AdminDashboardService:

    # =========================================================
    # DATE RANGE
    # =========================================================

    @staticmethod
    def get_date_range(
        period=None,
        start_date=None,
        end_date=None,
    ):
        today = timezone.localdate()

        logger.info(
            "Dashboard date request | period=%s | "
            "start=%s | end=%s | today=%s",
            period,
            start_date,
            end_date,
            today,
        )

        # -----------------------------------------------------
        # CUSTOM DATE RANGE
        # -----------------------------------------------------

        if start_date and end_date:

            if start_date > end_date:
                logger.warning(
                    "Invalid dashboard date range | "
                    "start=%s | end=%s",
                    start_date,
                    end_date,
                )

                raise ValidationError({
                    "date": (
                        "start_date cannot be greater "
                        "than end_date."
                    )
                })

            logger.info(
                "Using custom date range | %s -> %s",
                start_date,
                end_date,
            )

            return start_date, end_date

        # -----------------------------------------------------
        # TODAY
        # -----------------------------------------------------

        if period == "today":

            logger.info(
                "Using dashboard period TODAY | %s",
                today,
            )

            return today, today

        # -----------------------------------------------------
        # 7 DAYS
        # -----------------------------------------------------

        if period == "7d":

            start = today - timedelta(days=6)

            logger.info(
                "Using dashboard period 7D | %s -> %s",
                start,
                today,
            )

            return start, today

        # -----------------------------------------------------
        # 15 DAYS
        # -----------------------------------------------------

        if period == "15d":

            start = today - timedelta(days=14)

            logger.info(
                "Using dashboard period 15D | %s -> %s",
                start,
                today,
            )

            return start, today

        # -----------------------------------------------------
        # 30 DAYS
        # -----------------------------------------------------

        if period == "30d" or not period:

            start = today - timedelta(days=29)

            logger.info(
                "Using dashboard period 30D | %s -> %s",
                start,
                today,
            )

            return start, today

        # -----------------------------------------------------
        # INVALID PERIOD
        # -----------------------------------------------------

        logger.error(
            "Invalid dashboard period: %s",
            period,
        )

        raise ValidationError({
            "period": (
                "Invalid period. "
                "Use today, 7d, 15d or 30d."
            )
        })

    # =========================================================
    # DATETIME RANGE
    # =========================================================

    @staticmethod
    def get_datetime_range(
        start_date,
        end_date,
    ):
        """
        Convert local calendar dates into timezone-aware
        datetime boundaries.

        Example:

        start:
            2026-09-04 00:00:00 IST

        end:
            2026-10-04 00:00:00 IST

        The end datetime is EXCLUSIVE.
        """

        current_timezone = timezone.get_current_timezone()

        start_datetime = timezone.make_aware(
            datetime.combine(
                start_date,
                time.min,
            ),
            timezone=current_timezone,
        )

        end_datetime = timezone.make_aware(
            datetime.combine(
                end_date + timedelta(days=1),
                time.min,
            ),
            timezone=current_timezone,
        )

        logger.info(
            "Datetime range | %s -> %s",
            start_datetime,
            end_datetime,
        )

        return (
            start_datetime,
            end_datetime,
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    @staticmethod
    def get_summary(
        start_date,
        end_date,
    ):

        start_datetime, end_datetime = (
            AdminDashboardService.get_datetime_range(
                start_date,
                end_date,
            )
        )

        # -----------------------------------------------------
        # TOTAL ORDERS
        # -----------------------------------------------------

        total_orders = (
            Order.objects
            .filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime,
            )
            .count()
        )

        logger.info(
            "Total orders: %s",
            total_orders,
        )

        # -----------------------------------------------------
        # TOTAL CUSTOMERS
        # -----------------------------------------------------

        total_users = (
            User.objects
            .filter(
                role=User.Role.CUSTOMER,
            )
            .count()
        )

        logger.info(
            "Total customers: %s",
            total_users,
        )

        # -----------------------------------------------------
        # NEW CUSTOMERS
        # -----------------------------------------------------

        new_users = (
            User.objects
            .filter(
                role=User.Role.CUSTOMER,
                created_at__gte=start_datetime,
                created_at__lt=end_datetime,
            )
            .count()
        )

        logger.info(
            "New customers: %s",
            new_users,
        )

        # -----------------------------------------------------
        # PROCESSING ORDERS
        # -----------------------------------------------------
        #
        # Current Order model does not have PENDING.
        # PROCESSING is therefore used as pending_orders.
        #

        pending_orders = (
            Order.objects
            .filter(
                status=Order.Status.PROCESSING,
            )
            .count()
        )

        logger.info(
            "Processing / pending orders: %s",
            pending_orders,
        )

        result = {
            "total_orders": total_orders,
            "total_users": total_users,
            "new_users": new_users,
            "pending_orders": pending_orders,
        }

        logger.info(
            "Dashboard summary result: %s",
            result,
        )

        return result

    # =========================================================
    # ORDERS TREND
    # =========================================================

    @staticmethod
    def get_orders_trend(
        start_date,
        end_date,
    ):
        """
        Returns orders grouped by LOCAL calendar date.

        We intentionally do NOT use TruncDate() here because
        database-side timezone truncation was returning:

            {"date": null, "orders": 13}

        Instead, we fetch created_at values and convert them
        using Django's active timezone in Python.
        """

        start_datetime, end_datetime = (
            AdminDashboardService.get_datetime_range(
                start_date,
                end_date,
            )
        )

        orders = (
            Order.objects
            .filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime,
            )
            .values_list(
                "created_at",
                flat=True,
            )
        )

        order_count = len(orders)

        logger.info(
            "Orders matching trend: %s",
            order_count,
        )

        # -----------------------------------------------------
        # Initialize every date with 0
        # -----------------------------------------------------

        trend = {}

        current_date = start_date

        while current_date <= end_date:

            trend[current_date] = 0

            current_date += timedelta(days=1)

        # -----------------------------------------------------
        # Count orders by LOCAL date
        # -----------------------------------------------------

        for created_at in orders:

            if timezone.is_naive(created_at):
                created_at = timezone.make_aware(
                    created_at,
                    timezone=timezone.get_current_timezone(),
                )

            local_datetime = timezone.localtime(
                created_at,
                timezone=timezone.get_current_timezone(),
            )

            local_date = local_datetime.date()

            if local_date in trend:
                trend[local_date] += 1

        # -----------------------------------------------------
        # Convert dictionary into API response
        # -----------------------------------------------------

        result = [
            {
                "date": date,
                "orders": count,
            }
            for date, count in trend.items()
        ]

        logger.info(
            "Orders trend result: %s",
            result,
        )

        return result

    # =========================================================
    # ORDERS BY STATUS
    # =========================================================

    @staticmethod
    def get_orders_by_status(
        start_date,
        end_date,
    ):

        start_datetime, end_datetime = (
            AdminDashboardService.get_datetime_range(
                start_date,
                end_date,
            )
        )

        queryset = (
            Order.objects
            .filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime,
            )
        )

        matching_orders = queryset.count()

        logger.info(
            "Orders for status chart: %s",
            matching_orders,
        )

        data = (
            queryset
            .values("status")
            .annotate(
                count=Count("id"),
            )
            .order_by("status")
        )

        result = list(data)

        logger.info(
            "Orders by status: %s",
            result,
        )

        return result

    # =========================================================
    # RECENT ORDERS
    # =========================================================

    @staticmethod
    def get_recent_orders(
        limit=5,
    ):

        orders = (
            Order.objects
            .select_related(
                "customer",
                "customer__user",
            )
            .order_by(
                "-created_at",
            )[:limit]
        )

        result = list(orders)

        logger.info(
            "Recent orders count: %s",
            len(result),
        )

        for order in result:

            logger.info(
                "Recent order | "
                "id=%s | "
                "order_number=%s | "
                "customer=%s | "
                "status=%s | "
                "created_at=%s",
                order.id,
                order.order_number,
                order.customer_id,
                order.status,
                order.created_at,
            )

        return result

    # =========================================================
    # CUSTOMER REGISTRATIONS
    # =========================================================

    @staticmethod
    def get_user_registrations(
        start_date,
        end_date,
    ):
        """
        Returns customer registrations grouped by LOCAL date.

        The selected dashboard period is used so that:

            summary.new_users

        and:

            new_user_registrations

        represent the same date range.
        """

        start_datetime, end_datetime = (
            AdminDashboardService.get_datetime_range(
                start_date,
                end_date,
            )
        )

        logger.info(
            "Customer registration range | "
            "%s -> %s",
            start_datetime,
            end_datetime,
        )

        users = (
            User.objects
            .filter(
                role=User.Role.CUSTOMER,
                created_at__gte=start_datetime,
                created_at__lt=end_datetime,
            )
            .values_list(
                "created_at",
                flat=True,
            )
        )

        user_count = len(users)

        logger.info(
            "Customers registered in selected period: %s",
            user_count,
        )

        # -----------------------------------------------------
        # Initialize every date with 0
        # -----------------------------------------------------

        registrations = {}

        current_date = start_date

        while current_date <= end_date:

            registrations[current_date] = 0

            current_date += timedelta(days=1)

        # -----------------------------------------------------
        # Count users by LOCAL date
        # -----------------------------------------------------

        for created_at in users:

            if timezone.is_naive(created_at):
                created_at = timezone.make_aware(
                    created_at,
                    timezone=timezone.get_current_timezone(),
                )

            local_datetime = timezone.localtime(
                created_at,
                timezone=timezone.get_current_timezone(),
            )

            local_date = local_datetime.date()

            if local_date in registrations:
                registrations[local_date] += 1

        # -----------------------------------------------------
        # Convert dictionary into API response
        # -----------------------------------------------------

        result = [
            {
                "date": date,
                "users": count,
            }
            for date, count in registrations.items()
        ]

        logger.info(
            "Customer registration graph: %s",
            result,
        )

        return result

    # =========================================================
    # TOP CUSTOMERS
    # LAST 15 DAYS
    # =========================================================

    @staticmethod
    def get_top_users(
        days=15,
        limit=5,
    ):

        today = timezone.localdate()

        start_date = (
            today - timedelta(
                days=days - 1,
            )
        )

        start_datetime, end_datetime = (
            AdminDashboardService.get_datetime_range(
                start_date,
                today,
            )
        )

        logger.info(
            "Top customer range | "
            "%s -> %s | limit=%s",
            start_datetime,
            end_datetime,
            limit,
        )

        queryset = (
            Order.objects
            .filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime,
                customer__user__role=User.Role.CUSTOMER,
            )
        )

        matching_orders = queryset.count()

        logger.info(
            "Orders for top customers: %s",
            matching_orders,
        )

        data = (
            queryset
            .values(
                "customer_id",
                "customer__user__first_name",
                "customer__user__last_name",
                "customer__user__phone_number",
            )
            .annotate(
                orders=Count("id"),
            )
            .order_by(
                "-orders",
            )[:limit]
        )

        result = list(data)

        logger.info(
            "Top customers: %s",
            result,
        )

        return result

    # =========================================================
    # COMPLETE DASHBOARD
    # =========================================================

    @staticmethod
    def get_dashboard(
        period=None,
        start_date=None,
        end_date=None,
    ):

        logger.info(
            "========================================"
        )

        logger.info(
            "ADMIN DASHBOARD REQUEST START"
        )

        logger.info(
            "Input parameters | "
            "period=%s | "
            "start_date=%s | "
            "end_date=%s",
            period,
            start_date,
            end_date,
        )

        # -----------------------------------------------------
        # DATE RANGE
        # -----------------------------------------------------

        start_date, end_date = (
            AdminDashboardService.get_date_range(
                period=period,
                start_date=start_date,
                end_date=end_date,
            )
        )

        logger.info(
            "Final dashboard date range | "
            "%s -> %s",
            start_date,
            end_date,
        )

        # -----------------------------------------------------
        # SUMMARY
        # -----------------------------------------------------

        summary = (
            AdminDashboardService.get_summary(
                start_date=start_date,
                end_date=end_date,
            )
        )

        # -----------------------------------------------------
        # ORDERS TREND
        # -----------------------------------------------------

        orders_trend = (
            AdminDashboardService.get_orders_trend(
                start_date=start_date,
                end_date=end_date,
            )
        )

        # -----------------------------------------------------
        # ORDERS BY STATUS
        # -----------------------------------------------------

        orders_by_status = (
            AdminDashboardService.get_orders_by_status(
                start_date=start_date,
                end_date=end_date,
            )
        )

        # -----------------------------------------------------
        # RECENT ORDERS
        # -----------------------------------------------------

        recent_orders = (
            AdminDashboardService.get_recent_orders(
                limit=5,
            )
        )

        # -----------------------------------------------------
        # CUSTOMER REGISTRATIONS
        # -----------------------------------------------------
        #
        # IMPORTANT:
        # Use the same selected dashboard period.
        #

        user_registrations = (
            AdminDashboardService.get_user_registrations(
                start_date=start_date,
                end_date=end_date,
            )
        )

        # -----------------------------------------------------
        # TOP CUSTOMERS
        #
        # Currently this remains last 15 days.
        # -----------------------------------------------------

        top_users = (
            AdminDashboardService.get_top_users(
                days=15,
                limit=5,
            )
        )

        # -----------------------------------------------------
        # FINAL RESPONSE
        # -----------------------------------------------------

        result = {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },

            "summary": summary,

            "orders_trend": orders_trend,

            "orders_by_status": orders_by_status,

            "recent_orders": recent_orders,

            "new_user_registrations": user_registrations,

            "top_users": top_users,
        }

        # -----------------------------------------------------
        # FINAL LOG
        # -----------------------------------------------------

        logger.info(
            "Dashboard final summary | %s",
            {
                "total_orders": summary["total_orders"],
                "total_users": summary["total_users"],
                "new_users": summary["new_users"],
                "pending_orders": summary["pending_orders"],
                "trend_count": len(orders_trend),
                "status_count": len(orders_by_status),
                "recent_orders": len(recent_orders),
                "registration_days": len(user_registrations),
                "top_users": len(top_users),
            },
        )

        logger.info(
            "ADMIN DASHBOARD REQUEST END"
        )

        logger.info(
            "========================================"
        )

        return result