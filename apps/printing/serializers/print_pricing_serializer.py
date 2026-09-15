from rest_framework import serializers

from apps.printing.models.print_pricing import PrintPricing


class PrintPricingSerializer(serializers.ModelSerializer):

    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )

    class Meta:
        model = PrintPricing

        fields = [
            "id",
            "service",
            "service_name",
            "color_type",
            "paper_size",
            "print_side",
            "price_per_page",
            "minimum_charge",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "service_name",
            "created_at",
            "updated_at",
        ]