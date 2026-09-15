from rest_framework import serializers

from apps.printing.models.print_order import PrintOrder
from apps.printing.serializers.print_document_serializer import (
    PrintDocumentCreateSerializer,
    PrintDocumentSerializer,
)


class CreatePrintOrderSerializer(serializers.Serializer):

    documents = PrintDocumentCreateSerializer(
        many=True,
        required=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate_documents(self, value):

        if not value:
            raise serializers.ValidationError(
                "At least one document is required."
            )

        return value


class UpdatePrintOrderStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=PrintOrder.Status.choices,
    )


class PrintOrderSerializer(serializers.ModelSerializer):

    documents = PrintDocumentSerializer(
        many=True,
        read_only=True,
    )

    customer = serializers.SerializerMethodField()

    class Meta:
        model = PrintOrder

        fields = [
            "id",
            "order_number",
            "customer",
            "status",
            "payment_method",
            "payment_status",
            "subtotal",
            "delivery_fee",
            "discount",
            "total_amount",
            "notes",
            "documents",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_customer(self, obj):

        user = obj.customer.user

        return {
            "id": str(obj.customer.id),
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
        }