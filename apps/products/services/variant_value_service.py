from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.products.models.variant import (
    VariantAttribute,
    VariantValue,
)


class VariantValueService:

    @staticmethod
    @transaction.atomic
    def create_value(
        *,
        attribute,
        value,
    ):
        value = value.strip()

        if not value:
            raise ValidationError({
                "value": "Variant value cannot be empty."
            })

        # Make sure attribute exists and is active
        try:
            attribute_obj = VariantAttribute.objects.get(
                id=attribute,
                is_active=True,
            )
        except VariantAttribute.DoesNotExist:
            raise ValidationError({
                "attribute": "Invalid or inactive variant attribute."
            })

        # Prevent duplicate values under same attribute
        if VariantValue.objects.filter(
            attribute=attribute_obj,
            value__iexact=value,
        ).exists():
            raise ValidationError({
                "value": "This value already exists for this attribute."
            })

        variant_value = VariantValue.objects.create(
            attribute=attribute_obj,
            value=value,
        )

        return variant_value