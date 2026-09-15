from django.db import transaction
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.brands.models.brand import Brand

class BrandService:

    @staticmethod
    @transaction.atomic
    def create_brand(
        *,
        name,
        slug=None,
        description=None,
        logo_url=None,
    ):
        name = name.strip()

        if not name:
            raise ValidationError({
                "name": "Brand name cannot be empty."
            })

        slug = slugify(slug or name)

        if Brand.objects.filter(
            name__iexact=name
        ).exists():
            raise ValidationError({
                "name": "A brand with this name already exists."
            })

        if Brand.objects.filter(
            slug=slug
        ).exists():
            raise ValidationError({
                "slug": "A brand with this slug already exists."
            })

        brand = Brand.objects.create(
            name=name,
            slug=slug,
            description=description,
            logo_url=logo_url,
        )

        return brand