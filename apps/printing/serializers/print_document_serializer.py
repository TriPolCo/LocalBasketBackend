from rest_framework import serializers

from apps.printing.models.print_document import PrintDocument


class PrintDocumentCreateSerializer(serializers.Serializer):

    service = serializers.UUIDField()

    file_name = serializers.CharField(
        max_length=255,
    )

    file_url = serializers.URLField(
        max_length=1000,
    )

    cloudinary_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    file_type = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    file_size = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    page_count = serializers.IntegerField(
        min_value=1,
    )

    color_type = serializers.ChoiceField(
        choices=PrintDocument.ColorType.choices,
        default=PrintDocument.ColorType.BLACK_WHITE,
    )

    paper_size = serializers.ChoiceField(
        choices=PrintDocument.PaperSize.choices,
        default=PrintDocument.PaperSize.A4,
    )

    print_side = serializers.ChoiceField(
        choices=PrintDocument.PrintSide.choices,
        default=PrintDocument.PrintSide.SINGLE,
    )

    copies = serializers.IntegerField(
        min_value=1,
        default=1,
    )

    page_start = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )

    page_end = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )


class PrintDocumentSerializer(serializers.ModelSerializer):

    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )

    pricing = serializers.SerializerMethodField()

    class Meta:
        model = PrintDocument

        fields = [
            "id",
            "service",
            "service_name",

            "file_name",
            "file_url",
            "cloudinary_public_id",
            "file_type",
            "file_size",

            "page_count",
            "color_type",
            "paper_size",
            "print_side",
            "copies",

            "page_start",
            "page_end",

            "pricing",

            "price_per_page",
            "total_amount",

            "display_order",
            "created_at",
        ]

        read_only_fields = fields

    def get_pricing(self, obj):

        # If no page range is selected,
        # all pages are printed.
        if (
            obj.page_start is None
            and obj.page_end is None
        ):
            selected_pages = obj.page_count

        else:
            selected_pages = (
                obj.page_end
                - obj.page_start
                + 1
            )

        total_pages = (
            selected_pages * obj.copies
        )

        return {
            "price_per_page": str(
                obj.price_per_page
            ),
            "selected_pages": selected_pages,
            "copies": obj.copies,
            "total_pages": total_pages,
            "total_amount": str(
                obj.total_amount
            ),
        }