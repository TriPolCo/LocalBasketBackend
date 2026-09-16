from rest_framework import serializers

from apps.products.models.product import Product


class ProductSearchSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    category_id = serializers.UUIDField(
        source="category.id",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    subcategory_id = serializers.UUIDField(
        source="subcategory.id",
        read_only=True,
    )

    subcategory_name = serializers.CharField(
        source="subcategory.name",
        read_only=True,
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "image_url",
            "category_id",
            "category_name",
            "subcategory_id",
            "subcategory_name",
        ]

        read_only_fields = fields

    def get_image_url(self, obj):
        """
        Return only one image.
        Priority:
        1. Primary image
        2. First image
        """

        variant = (
            obj.variants
            .filter(is_active=True)
            .prefetch_related("images")
            .first()
        )

        if not variant:
            return None

        primary_image = (
            variant.images
            .filter(is_primary=True)
            .first()
        )

        if primary_image:
            return primary_image.image_url

        first_image = variant.images.first()

        if first_image:
            return first_image.image_url

        return None