# apps/food/views/food_setting_view.py
from datetime import datetime, time
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.food.models.food_setting import FoodSetting


def parse_time_input(val):
    """Safely parse time string from request into time object."""
    if isinstance(val, time):
        return val
    if isinstance(val, str):
        val = val.strip()
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(val, fmt).time()
            except ValueError:
                pass
    return None


# ========================================================
# 1. PUBLIC GET: Customer Website / Mobile App
# ========================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def get_food_store_status(request):
    setting = FoodSetting.get_settings()

    open_str = (
        setting.opening_time.strftime("%H:%M")
        if isinstance(setting.opening_time, time)
        else str(setting.opening_time)[:5]
    )
    close_str = (
        setting.closing_time.strftime("%H:%M")
        if isinstance(setting.closing_time, time)
        else str(setting.closing_time)[:5]
    )

    return Response(
        {
            "success": True,
            "data": {
                "is_open": setting.is_currently_open,
                "is_manually_open": setting.is_open,
                "opening_time": open_str,
                "closing_time": close_str,
                "closed_message": setting.closed_message,
            },
        },
        status=status.HTTP_200_OK,
    )


# ========================================================
# 2. ADMIN PATCH: Admin Updates Time or Closes Kitchen
# ========================================================
@api_view(["PATCH", "POST"])
@permission_classes([IsAuthenticated])
def admin_update_food_store_status(request):
    setting = FoodSetting.get_settings()

    # Admin toggles open/closed manually
    if "is_open" in request.data:
        val = request.data.get("is_open")
        setting.is_open = val if isinstance(val, bool) else str(val).lower() in ["true", "1"]

    # Admin changes opening/closing hours
    if "opening_time" in request.data:
        parsed = parse_time_input(request.data.get("opening_time"))
        if parsed:
            setting.opening_time = parsed

    if "closing_time" in request.data:
        parsed = parse_time_input(request.data.get("closing_time"))
        if parsed:
            setting.closing_time = parsed

    if "closed_message" in request.data:
        setting.closed_message = str(request.data.get("closed_message")).strip()

    setting.save()

    open_str = (
        setting.opening_time.strftime("%H:%M")
        if isinstance(setting.opening_time, time)
        else str(setting.opening_time)[:5]
    )
    close_str = (
        setting.closing_time.strftime("%H:%M")
        if isinstance(setting.closing_time, time)
        else str(setting.closing_time)[:5]
    )

    return Response(
        {
            "success": True,
            "message": "Food store settings updated successfully.",
            "data": {
                "is_open": setting.is_currently_open,
                "is_manually_open": setting.is_open,
                "opening_time": open_str,
                "closing_time": close_str,
                "closed_message": setting.closed_message,
            },
        },
        status=status.HTTP_200_OK,
    )