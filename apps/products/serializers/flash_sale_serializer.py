from rest_framework import serializers

from apps.products.models.variant import ProductVariant


class FlashSaleProductSerializer(serializers.ModelSerializer):

    variant_id = serializers.UUIDField(
        source="id",
        read_only=True
    )

    product_id = serializers.UUIDField(
        source="product.id",
        read_only=True
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    image_url = serializers.SerializerMethodField()

    discount_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ProductVariant

        fields = [
            "variant_id",
            "product_id",
            "product_name",
            "sku",
            "mrp",
            "selling_price",
            "discount_percentage",
            "image_url",
        ]

        read_only_fields = fields

    def get_image_url(self, obj):

        primary_image = (
            obj.images
            .filter(is_primary=True)
            .first()
        )

        if primary_image:
            return primary_image.image_url

        first_image = obj.images.first()

        if first_image:
            return first_image.image_url

        return None