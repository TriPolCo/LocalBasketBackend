from rest_framework import serializers

from apps.products.models.product import Product


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "subcategory",
            "brand",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        return {
            "id": str(obj.category.id),
            "name": obj.category.name,
        }

    def get_subcategory(self, obj):
        return {
            "id": str(obj.subcategory.id),
            "name": obj.subcategory.name,
        }

    def get_brand(self, obj):
        if not obj.brand:
            return None

        return {
            "id": str(obj.brand.id),
            "name": obj.brand.name,
        }

    def get_image(self, obj):
        """
        Return only ONE primary image for the product.

        The image comes from the first active variant
        that has a primary image.
        """

        for variant in obj.variants.all():
            image = variant.images.filter(
                is_primary=True
            ).first()

            if image:
                return {
                    "id": str(image.id),
                    "image_url": image.image_url,
                    "cloudinary_public_id": image.cloudinary_public_id,
                }

        return None