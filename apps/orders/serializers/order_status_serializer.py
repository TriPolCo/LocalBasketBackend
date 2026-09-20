from rest_framework import serializers
from apps.orders.models.order import Order


class AdminOrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Order.Status.choices
    )