from django.utils.text import slugify
from rest_framework import serializers

from apps.products.models.product import Product
from apps.products.models.variant import (
    VariantValue,
    ProductVariantValue,
    ProductVariantImage,
    ProductVariant,
)


# ============================================================
# PRODUCT VARIANT IMAGE
# ============================================================

class ProductVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = [
            "id",
            "cloudinary_public_id",
            "image_url",
            "is_primary",
            "display_order",
        ]


# ============================================================
# PRODUCT VARIANT ATTRIBUTE / VALUE
# ============================================================

class ProductVariantValueSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariantValue
        fields = [
            "id",
            "attribute",
            "value",
        ]

    def get_attribute(self, obj):
        value = obj.value
        attribute = value.attribute

        return {
            "id": str(attribute.id),
            "name": attribute.name,
            "code": attribute.code,
        }

    def get_value(self, obj):
        value = obj.value

        return {
            "id": str(value.id),
            "value": value.value,
            "is_active": value.is_active,
        }


# ============================================================
# PRODUCT VARIANT RESPONSE
# ============================================================

class ProductVariantSerializer(serializers.ModelSerializer):

    attributes = ProductVariantValueSerializer(
        source="variant_values",
        many=True,
        read_only=True,
    )

    images = ProductVariantImageSerializer(
        many=True,
        read_only=True,
    )

    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant

        fields = [
            "id",
            "sku",
            "mrp",
            "selling_price",
            "stock",
            "is_active",
            "attributes",
            "primary_image",
            "images",
            "created_at",
            "updated_at",
        ]

    def get_primary_image(self, obj):

        for image in obj.images.all():

            if image.is_primary:
                return {
                    "id": str(image.id),
                    "image_url": image.image_url,
                    "cloudinary_public_id": (
                        image.cloudinary_public_id
                    ),
                }

        return None


# ============================================================
# PRODUCT VARIANT IMAGE INPUT
# ============================================================

class ProductVariantImageInputSerializer(serializers.Serializer):

    cloudinary_public_id = serializers.CharField(
        max_length=255
    )

    image_url = serializers.URLField(
        max_length=1000
    )

    is_primary = serializers.BooleanField(
        default=False
    )

    display_order = serializers.IntegerField(
        min_value=0,
        default=0
    )


# ============================================================
# PRODUCT VARIANT ATTRIBUTE INPUT
# ============================================================

class ProductVariantAttributeInputSerializer(serializers.Serializer):

    attribute = serializers.UUIDField()

    value = serializers.UUIDField()

    def validate(self, attrs):

        try:
            variant_value = (
                VariantValue.objects
                .select_related("attribute")
                .get(
                    id=attrs["value"],
                    is_active=True,
                )
            )

        except VariantValue.DoesNotExist:

            raise serializers.ValidationError({
                "value": (
                    "Invalid or inactive variant value."
                )
            })

        # Make sure selected value belongs
        # to selected attribute.
        if variant_value.attribute_id != attrs["attribute"]:

            raise serializers.ValidationError({
                "value": (
                    "The selected value does not belong "
                    "to the selected attribute."
                )
            })

        return attrs


# ============================================================
# PRODUCT VARIANT CREATE
# ============================================================

class ProductVariantCreateSerializer(serializers.Serializer):

    sku = serializers.CharField(
        max_length=100
    )

    mrp = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0
    )

    selling_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0
    )

    stock = serializers.IntegerField(
        min_value=0
    )

    attributes = ProductVariantAttributeInputSerializer(
        many=True,
        allow_empty=False
    )

    images = ProductVariantImageInputSerializer(
        many=True,
        allow_empty=False
    )

    def validate_sku(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "SKU cannot be empty."
            )

        return value

    def validate(self, attrs):

        mrp = attrs["mrp"]
        selling_price = attrs["selling_price"]

        # --------------------------------------------------
        # Selling price cannot exceed MRP
        # --------------------------------------------------

        if selling_price > mrp:

            raise serializers.ValidationError({
                "selling_price": (
                    "Selling price cannot be greater than MRP."
                )
            })

        # --------------------------------------------------
        # Duplicate attributes
        # --------------------------------------------------

        attributes = attrs["attributes"]

        attribute_ids = [
            item["attribute"]
            for item in attributes
        ]

        if len(attribute_ids) != len(set(attribute_ids)):

            raise serializers.ValidationError({
                "attributes": (
                    "A variant cannot contain the same "
                    "attribute more than once."
                )
            })

        # --------------------------------------------------
        # Primary images
        # --------------------------------------------------

        images = attrs["images"]

        primary_images = [
            image
            for image in images
            if image.get("is_primary", False)
        ]

        if len(primary_images) > 1:

            raise serializers.ValidationError({
                "images": (
                    "A variant can have only one "
                    "primary image."
                )
            })

        if len(primary_images) == 0:

            raise serializers.ValidationError({
                "images": (
                    "A variant must have one "
                    "primary image."
                )
            })

        return attrs


# ============================================================
# PRODUCT CREATE
# ============================================================

class ProductCreateSerializer(serializers.ModelSerializer):

    variants = ProductVariantCreateSerializer(
        many=True,
        allow_empty=False
    )

    class Meta:

        model = Product

        fields = [
            "name",
            "slug",
            "description",
            "category",
            "subcategory",
            "brand",
            "is_active",
            "variants",
        ]

        extra_kwargs = {
            "slug": {
                "required": False,
                "allow_blank": True,
            },
            "description": {
                "required": False,
                "allow_blank": True,
            },
            "brand": {
                "required": False,
                "allow_null": True,
            },
            "is_active": {
                "required": False,
            },
        }

    def validate_name(self, value):

        value = value.strip()

        if not value:

            raise serializers.ValidationError(
                "Product name cannot be empty."
            )

        return value

    def validate_slug(self, value):

        value = value.strip()

        if value:
            value = slugify(value)

        return value

    def validate(self, attrs):

        category = attrs["category"]
        subcategory = attrs["subcategory"]

        # --------------------------------------------------
        # Category must be main category
        # --------------------------------------------------

        if category.parent_id is not None:

            raise serializers.ValidationError({
                "category": (
                    "Selected category must be "
                    "a main category."
                )
            })

        # --------------------------------------------------
        # Subcategory must be child
        # --------------------------------------------------

        if subcategory.parent_id is None:

            raise serializers.ValidationError({
                "subcategory": (
                    "Selected subcategory must "
                    "be a subcategory."
                )
            })

        # --------------------------------------------------
        # Subcategory must belong to category
        # --------------------------------------------------

        if subcategory.parent_id != category.id:

            raise serializers.ValidationError({
                "subcategory": (
                    "Selected subcategory does not "
                    "belong to the selected category."
                )
            })

        # --------------------------------------------------
        # Generate slug
        # --------------------------------------------------

        slug = attrs.get("slug")

        if not slug:

            slug = slugify(attrs["name"])

            attrs["slug"] = slug

        # --------------------------------------------------
        # Check duplicate slug
        # --------------------------------------------------

        if Product.objects.filter(
            slug=slug
        ).exists():

            raise serializers.ValidationError({
                "slug": (
                    "A product with this slug "
                    "already exists."
                )
            })

        # --------------------------------------------------
        # Check duplicate SKUs inside request
        # --------------------------------------------------

        variants = attrs["variants"]

        skus = [
            variant["sku"]
            for variant in variants
        ]

        if len(skus) != len(set(skus)):

            raise serializers.ValidationError({
                "variants": (
                    "Duplicate SKU found in variants."
                )
            })

        # --------------------------------------------------
        # Check SKU already exists in database
        # --------------------------------------------------

        existing_skus = ProductVariant.objects.filter(
            sku__in=skus
        ).values_list(
            "sku",
            flat=True
        )

        existing_skus = list(existing_skus)

        if existing_skus:

            raise serializers.ValidationError({
                "variants": (
                    "The following SKU(s) already exist: "
                    + ", ".join(existing_skus)
                )
            })

        return attrs


# ============================================================
# PRODUCT CREATE RESPONSE
# ============================================================

class ProductCreateResponseSerializer(
    serializers.ModelSerializer
):

    category = serializers.SerializerMethodField()

    subcategory = serializers.SerializerMethodField()

    brand = serializers.SerializerMethodField()

    variants = ProductVariantSerializer(
        many=True,
        read_only=True,
    )

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
            "variants",
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

        for variant in obj.variants.all():

            for image in variant.images.all():

                if image.is_primary:

                    return {
                        "id": str(image.id),
                        "image_url": image.image_url,
                        "cloudinary_public_id": (
                            image.cloudinary_public_id
                        ),
                    }

        return None


# ============================================================
# PRODUCT LIST
# ============================================================

class ProductListSerializer(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()

    subcategory = serializers.SerializerMethodField()

    brand = serializers.SerializerMethodField()

    # One product-level primary image
    image = serializers.SerializerMethodField()

    # All variants
    variants = ProductVariantSerializer(
        many=True,
        read_only=True,
    )

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

            "variants",

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
        Return ONE primary image for the product.

        It takes the first primary image found
        across the product's variants.
        """

        for variant in obj.variants.all():

            for image in variant.images.all():

                if image.is_primary:

                    return {
                        "id": str(image.id),
                        "image_url": image.image_url,
                        "cloudinary_public_id": (
                            image.cloudinary_public_id
                        ),
                    }

        return None