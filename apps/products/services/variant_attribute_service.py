from django.db import transaction
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.products.models.variant import VariantAttribute


class VariantAttributeService:

    @staticmethod
    @transaction.atomic
    def create_attribute(
        *,
        name,
        code=None,
        is_active=True,
    ):
        name = name.strip()

        if not name:
            raise ValidationError({
                "name": "Attribute name cannot be empty."
            })

        if not code:
            code = slugify(name)
        else:
            code = slugify(code)

        # Duplicate name check
        if VariantAttribute.objects.filter(
            name__iexact=name
        ).exists():
            raise ValidationError({
                "name": "An attribute with this name already exists."
            })

        # Duplicate code check
        if VariantAttribute.objects.filter(
            code=code
        ).exists():
            raise ValidationError({
                "code": "An attribute with this code already exists."
            })

        attribute = VariantAttribute.objects.create(
            name=name,
            code=code,
            is_active=is_active,
        )

        return attribute

    @staticmethod
    def get_attributes(*, include_inactive=False):
        queryset = (
            VariantAttribute.objects
            .prefetch_related("values")
            .all()
        )

        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by("name")