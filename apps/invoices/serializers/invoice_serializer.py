from rest_framework import serializers
from apps.invoices.models.invoice import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "order",
            "order_number",
            "generated_at",
            "updated_at",
        ]
        read_only_fields = fields