from rest_framework import serializers

from apps.cart.models.cart_item import CartItem
from apps.cart.models.cart import Cart
from apps.products.models.variant import ProductVariant


class AddToCartSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField(
        required=True
    )

    quantity = serializers.IntegerField(
        required=True,
        min_value=1
    )

    def validate_variant_id(self, value):
        if not ProductVariant.objects.filter(
            id=value,
            is_active=True,
        ).exists():
            raise serializers.ValidationError(
                "Product variant not found or inactive."
            )

        return value


class UpdateCartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        required=True,
        min_value=1
    )


class CartItemSerializer(serializers.ModelSerializer):

    variant_id = serializers.UUIDField(
        source="variant.id",
        read_only=True
    )

    product_id = serializers.UUIDField(
        source="variant.product.id",
        read_only=True
    )

    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    sku = serializers.CharField(
        source="variant.sku",
        read_only=True
    )

    mrp = serializers.DecimalField(
        source="variant.mrp",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    selling_price = serializers.DecimalField(
        source="variant.selling_price",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    stock = serializers.IntegerField(
        source="variant.stock",
        read_only=True
    )

    item_total = serializers.SerializerMethodField()

    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem

        fields = [
            "id",
            "variant_id",
            "product_id",
            "product_name",
            "sku",
            "mrp",
            "selling_price",
            "stock",
            "quantity",
            "item_total",
            "primary_image",
            "created_at",
            "updated_at",
        ]

    def get_item_total(self, obj):
        return (
            obj.quantity *
            obj.variant.selling_price
        )

    def get_primary_image(self, obj):

        image = (
            obj.variant.images
            .filter(is_primary=True)
            .first()
        )

        if not image:
            image = obj.variant.images.first()

        if not image:
            return None

        return {
            "id": str(image.id),
            "image_url": image.image_url,
            "cloudinary_public_id": image.cloudinary_public_id,
        }


class CartSerializer(serializers.ModelSerializer):

    total_items = serializers.SerializerMethodField()

    total_quantity = serializers.SerializerMethodField()

    subtotal = serializers.SerializerMethodField()

    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Cart

        fields = [
            "id",
            "total_items",
            "total_quantity",
            "subtotal",
            "items",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.items.count()

    def get_total_quantity(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

    def get_subtotal(self, obj):
        return sum(
            item.quantity *
            item.variant.selling_price
            for item in obj.items.all()
        )