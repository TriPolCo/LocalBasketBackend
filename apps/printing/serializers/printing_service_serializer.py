from rest_framework import serializers

from apps.printing.models.printing_service import PrintingService
from apps.printing.serializers.print_pricing_serializer import (
    PrintPricingSerializer,
)


class PrintingServiceSerializer(serializers.ModelSerializer):
    pricing = serializers.SerializerMethodField()

    class Meta:
        model = PrintingService
        fields = [
            "id",
            "service_type",
            "name",
            "subtitle",
            "icon",
            "description",
            "is_active",
            "display_order",
            "pricing",
        ]
        read_only_fields = fields

    def get_pricing(self, obj):
        pricing = obj.pricing.filter(
            is_active=True
        ).order_by(
            "paper_size",
            "color_type",
            "print_side",
        )

        return PrintPricingSerializer(
            pricing,
            many=True,
        ).data