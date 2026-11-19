# apps/food/models/food_setting.py
from datetime import datetime, time
from django.db import models
from django.utils import timezone


class FoodSetting(models.Model):
    is_open = models.BooleanField(
        default=True,
        help_text="Master switch to manually open or close food orders."
    )

    opening_time = models.TimeField(
        default=time(7, 0),
        help_text="Time when food orders open (e.g., 07:00 AM)."
    )
    closing_time = models.TimeField(
        default=time(21, 0),
        help_text="Time when food orders close (e.g., 09:00 PM)."
    )

    closed_message = models.CharField(
        max_length=255,
        default="We are currently closed for food orders. Kitchen reopens at 7:00 AM.",
        help_text="Message displayed to customers when closed."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "food_settings"
        verbose_name = "Food Store Setting"

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(id=1)
        return settings

    @staticmethod
    def _to_time(val):
        """Converts string like '07:00' or '07:00:00' to a datetime.time object."""
        if isinstance(val, time):
            return val
        if isinstance(val, str):
            val = val.strip()
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    return datetime.strptime(val, fmt).time()
                except ValueError:
                    pass
        return time(7, 0)

    @property
    def is_currently_open(self):
        if not self.is_open:
            return False

        # ✅ Ensure both are converted to datetime.time objects before comparing
        open_t = self._to_time(self.opening_time)
        close_t = self._to_time(self.closing_time)
        now_time = timezone.localtime(timezone.now()).time()

        if open_t <= close_t:
            return open_t <= now_time <= close_t
        else:
            # Handles overnight hours (e.g. 7 PM to 2 AM)
            return now_time >= open_t or now_time <= close_t