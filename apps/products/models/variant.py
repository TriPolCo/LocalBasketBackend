import uuid

from django.db import models


class VariantAttribute(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=100,
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "variant_attributes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class VariantValue(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    attribute = models.ForeignKey(
        VariantAttribute,
        on_delete=models.CASCADE,
        related_name="values",
    )

    value = models.CharField(
        max_length=100,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "variant_values"
        ordering = ["value"]

        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_variant_value_per_attribute",
            ),
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="variants",
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
    )

    mrp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    stock = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "product_variants"
        ordering = ["-created_at"]

    def __str__(self):
        return self.sku


class ProductVariantValue(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="variant_values",
    )

    value = models.ForeignKey(
        VariantValue,
        on_delete=models.PROTECT,
        related_name="product_variant_values",
    )

    class Meta:
        db_table = "product_variant_values"

        constraints = [
            models.UniqueConstraint(
                fields=["variant", "value"],
                name="unique_product_variant_value",
            ),
        ]

    def __str__(self):
        return f"{self.variant.sku} - {self.value.value}"


class ProductVariantImage(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images",
    )

    cloudinary_public_id = models.CharField(
        max_length=255,
    )

    image_url = models.URLField(
        max_length=1000,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "product_variant_images"
        ordering = ["display_order", "created_at"]