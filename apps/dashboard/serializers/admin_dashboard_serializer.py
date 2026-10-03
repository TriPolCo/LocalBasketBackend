from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    pending_orders = serializers.IntegerField()


class OrdersTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    orders = serializers.IntegerField()


class OrdersStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class DashboardCustomerSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    phone_number = serializers.CharField(
        allow_null=True,
    )


class RecentOrderSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    order_number = serializers.CharField()
    customer = DashboardCustomerSerializer()
    created_at = serializers.DateTimeField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class UserRegistrationSerializer(serializers.Serializer):
    date = serializers.DateField()
    users = serializers.IntegerField()