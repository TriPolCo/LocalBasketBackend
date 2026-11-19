# apps/notifications/pusher_service.py
import json
import pusher
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

def get_pusher_client():
    app_id = getattr(settings, "PUSHER_APP_ID", None)
    key = getattr(settings, "PUSHER_KEY", None)
    secret = getattr(settings, "PUSHER_SECRET", None)
    cluster = getattr(settings, "PUSHER_CLUSTER", "ap2")

    if not app_id or app_id == "YOUR_APP_ID":
        print("⚠️ Pusher Warning: PUSHER_APP_ID is not configured in settings.py")
        return None

    return pusher.Pusher(
        app_id=str(app_id),
        key=key,
        secret=secret,
        cluster=cluster,
        ssl=True
    )

def trigger_admin_order_notification(order_data):
    """
    Broadcasts the newly placed order to React Admin Dashboard.
    Converts UUID, Decimal, and DateTime objects automatically to JSON.
    """
    try:
        client = get_pusher_client()
        if not client:
            return

        # 🔥 Safely convert UUID, Decimal, DateTime into standard JSON types
        safe_data = json.loads(json.dumps(order_data, cls=DjangoJSONEncoder))

        client.trigger(
            channels='admin-orders',
            event_name='new-order',
            data=safe_data
        )
        print(f"✅ Notification sent via WebSocket for Order #{safe_data.get('id', '')}")
    except Exception as e:
        print(f"Error sending WebSocket notification: {e}")