from django.utils.text import slugify
from rest_framework import serializers
from apps.brands.models.brand import Brand


class BrandCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = [
            "name",
            "slug",
            "description",
            "logo_url",
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
            "logo_url": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
        }

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Brand name cannot be empty."
            )

        return value

    def validate_slug(self, value):
        value = value.strip()

        if value:
            return slugify(value)

        return value

    def validate(self, attrs):
        name = attrs["name"]
        slug = attrs.get("slug")

        if not slug:
            attrs["slug"] = slugify(name)

        if Brand.objects.filter(
            name__iexact=name
        ).exists():
            raise serializers.ValidationError({
                "name": "A brand with this name already exists."
            })

        if Brand.objects.filter(
            slug=attrs["slug"]
        ).exists():
            raise serializers.ValidationError({
                "slug": "A brand with this slug already exists."
            })

        return attrs


class BrandResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo_url",
            "is_active",
            "created_at",
            "updated_at",
        ]