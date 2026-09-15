from rest_framework import serializers


class AdminLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
    )

    password = serializers.CharField(
        write_only=True,
    )