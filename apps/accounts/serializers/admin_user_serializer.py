from rest_framework import serializers

from apps.accounts.models.user import User


class AdminUserSerializer(serializers.ModelSerializer):

    customer_id = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "is_active",
            "phone_verified",
            "email_verified",
            "customer_id",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_customer_id(self, obj):

        if hasattr(obj, "customer_profile"):
            return str(obj.customer_profile.id)

        return None