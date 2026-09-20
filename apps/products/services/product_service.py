from django.db import transaction
from django.db.models import Count, Q
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404


from apps.products.models.product import Product

from apps.products.models.variant import (
    ProductVariant,
    ProductVariantValue,
    ProductVariantImage,
    VariantValue,
)


class ProductService:

    # ============================================================
    # CREATE PRODUCT
    # ============================================================

    @staticmethod
    @transaction.atomic
    def create_product(
        *,
        name,
        category,
        subcategory,
        variants,
        brand=None,
        slug=None,
        description=None,
        is_active=True,
    ):

        # ========================================================
        # CATEGORY VALIDATION
        # ========================================================

        if category.parent_id is not None:
            raise ValidationError({
                "category": (
                    "Selected category must be a main category."
                )
            })

        # ========================================================
        # SUBCATEGORY VALIDATION
        # ========================================================

        if subcategory.parent_id is None:
            raise ValidationError({
                "subcategory": (
                    "Selected subcategory must be a subcategory."
                )
            })

        if subcategory.parent_id != category.id:
            raise ValidationError({
                "subcategory": (
                    "Selected subcategory does not belong "
                    "to the selected category."
                )
            })

        # ========================================================
        # SLUG
        # ========================================================

        if not slug:
            slug = slugify(name)

        if not slug:
            raise ValidationError({
                "slug": "Unable to generate a valid product slug."
            })

        if Product.objects.filter(slug=slug).exists():
            raise ValidationError({
                "slug": (
                    "A product with this slug already exists."
                )
            })

        # ========================================================
        # CREATE PRODUCT
        # ========================================================

        product = Product.objects.create(
            name=name,
            slug=slug,
            description=description,
            category=category,
            subcategory=subcategory,
            brand=brand,
            is_active=is_active,
        )

        # ========================================================
        # CREATE VARIANTS
        # ========================================================

        for variant_data in variants:

            sku = variant_data["sku"]

            # ----------------------------------------------------
            # SKU UNIQUENESS
            # ----------------------------------------------------

            if ProductVariant.objects.filter(
                sku=sku
            ).exists():

                raise ValidationError({
                    "variants": (
                        f"SKU '{sku}' already exists."
                    )
                })

            # ----------------------------------------------------
            # CREATE PRODUCT VARIANT
            # ----------------------------------------------------

            variant = ProductVariant.objects.create(
                product=product,
                sku=sku,
                mrp=variant_data["mrp"],
                selling_price=variant_data["selling_price"],
                stock=variant_data["stock"],
                is_active=True,
            )

            # ====================================================
            # VARIANT VALUES
            # ====================================================

            attributes = variant_data["attributes"]

            value_ids = [
                attribute_data["value"]
                for attribute_data in attributes
            ]

            # ----------------------------------------------------
            # Fetch all values in one query
            # ----------------------------------------------------

            values = (
                VariantValue.objects
                .filter(
                    id__in=value_ids,
                    is_active=True,
                )
                .select_related("attribute")
            )

            values_map = {
                value.id: value
                for value in values
            }

            # ----------------------------------------------------
            # Make sure every value exists
            # ----------------------------------------------------

            if len(values_map) != len(value_ids):
                raise ValidationError({
                    "variants": (
                        f"Invalid or inactive variant values "
                        f"for SKU '{sku}'."
                    )
                })

            # ----------------------------------------------------
            # Create ProductVariantValue records
            # ----------------------------------------------------

            variant_values = []

            for attribute_data in attributes:

                attribute_id = attribute_data["attribute"]
                value_id = attribute_data["value"]

                value = values_map.get(value_id)

                if value is None:
                    raise ValidationError({
                        "variants": (
                            f"Variant value '{value_id}' "
                            f"is invalid for SKU '{sku}'."
                        )
                    })

                # ------------------------------------------------
                # Attribute/value relationship validation
                # ------------------------------------------------

                if value.attribute_id != attribute_id:

                    raise ValidationError({
                        "variants": (
                            f"Variant value '{value.value}' "
                            f"does not belong to the selected "
                            f"attribute for SKU '{sku}'."
                        )
                    })

                variant_values.append(
                    ProductVariantValue(
                        variant=variant,
                        value=value,
                    )
                )

            # ----------------------------------------------------
            # Bulk create variant values
            # ----------------------------------------------------

            ProductVariantValue.objects.bulk_create(
                variant_values
            )

            # ====================================================
            # IMAGES
            # ====================================================

            images = variant_data["images"]

            variant_images = []

            for image in images:

                variant_images.append(
                    ProductVariantImage(
                        variant=variant,
                        cloudinary_public_id=(
                            image["cloudinary_public_id"]
                        ),
                        image_url=image["image_url"],
                        is_primary=image.get(
                            "is_primary",
                            False
                        ),
                        display_order=image.get(
                            "display_order",
                            0
                        ),
                    )
                )

            # ----------------------------------------------------
            # Bulk create images
            # ----------------------------------------------------

            ProductVariantImage.objects.bulk_create(
                variant_images
            )

        # ========================================================
        # RETURN PRODUCT
        # ========================================================

        return product

    # ============================================================
    # GET PRODUCTS
    # ============================================================

    @staticmethod
    def get_products(category=None):

        queryset = (
            Product.objects
            .select_related(
                "category",
                "subcategory",
                "brand",
            )
            .prefetch_related(
                "variants",
                "variants__images",
                "variants__variant_values",
                "variants__variant_values__value",
                "variants__variant_values__value__attribute",
            )
            .filter(
                is_active=True,
            )
        )

        # --------------------------------------------------
        # Filter by category
        # --------------------------------------------------
        if category:
            queryset = queryset.filter(
                category__slug=category
            )

        return queryset.order_by("-created_at")

    @staticmethod
    def get_product_by_id(product_id):
        return get_object_or_404(
            Product.objects
            .select_related(
                "category",
                "subcategory",
                "brand",
            )
            .prefetch_related(
                "variants",
                "variants__images",
                "variants__variant_values",
                "variants__variant_values__value",
                "variants__variant_values__value__attribute",
            ),
            id=product_id,
            is_active=True,
        )

    @staticmethod
    def get_products_by_category(category_id):

        return (
            Product.objects
            .filter(
                category_id=category_id,
                is_active=True,
            )
            .select_related(
                "category",
                "subcategory",
                "brand",
            )
            .prefetch_related(
                "variants",
                "variants__images",
                "variants__variant_values__value__attribute",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_popular_products(limit=10):

        return (
            Product.objects
            .filter(
                is_active=True,
                variants__is_active=True,
            )
            .annotate(
                order_count=Count(
                    "variants__order_items__order",
                    filter=Q(
                        variants__order_items__order__status__in=[
                            "PROCESSING",
                            "SHIPPED",
                            "IN_TRANSIT",
                            "DELIVERED",
                        ]
                    ),
                    distinct=True,
                )
            )
            .filter(
                order_count__gt=0
            )
            .select_related(
                "category",
                "subcategory",
                "brand",
            )
            .prefetch_related(
                "variants",
                "variants__images",
                "variants__variant_values__value__attribute",
            )
            .order_by(
                "-order_count",
                "-created_at",
            )[:limit]
        )