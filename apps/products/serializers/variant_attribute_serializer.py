from django.utils.text import slugify
from rest_framework import serializers

from apps.products.models.variant import VariantAttribute,VariantValue


class VariantAttributeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantAttribute
        fields = [
            "name",
            "code",
            "is_active",
        ]
        extra_kwargs = {
            "code": {
                "required": False,
                "allow_blank": True,
            },
            "is_active": {
                "required": False,
            },
        }

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Attribute name cannot be empty."
            )

        return value

    def validate_code(self, value):
        value = value.strip()

        if value:
            return slugify(value)

        return value

    def validate(self, attrs):
        name = attrs["name"]
        code = attrs.get("code")

        # Generate code automatically if not provided
        if not code:
            attrs["code"] = slugify(name)

        # Check duplicate name
        if VariantAttribute.objects.filter(
            name__iexact=name
        ).exists():
            raise serializers.ValidationError({
                "name": "An attribute with this name already exists."
            })

        # Check duplicate code
        if VariantAttribute.objects.filter(
            code=attrs["code"]
        ).exists():
            raise serializers.ValidationError({
                "code": "An attribute with this code already exists."
            })

        return attrs





class VariantValueNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantValue
        fields = [
            "id",
            "value",
            "is_active",
        ]


class VariantAttributeResponseSerializer(serializers.ModelSerializer):
    values = VariantValueNestedSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = VariantAttribute
        fields = [
            "id",
            "name",
            "code",
            "is_active",
            "values",
            "created_at",
            "updated_at",
        ]