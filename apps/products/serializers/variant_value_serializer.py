from rest_framework import serializers

from apps.products.models.variant import (
    VariantAttribute,
    VariantValue,
)


class VariantValueCreateSerializer(serializers.ModelSerializer):
    attribute = serializers.UUIDField()

    class Meta:
        model = VariantValue
        fields = [
            "attribute",
            "value",
        ]

    def validate_attribute(self, value):
        try:
            attribute = VariantAttribute.objects.get(
                id=value,
                is_active=True,
            )
        except VariantAttribute.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or inactive variant attribute."
            )

        return attribute.id

    def validate_value(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Variant value cannot be empty."
            )

        return value

    def validate(self, attrs):
        attribute_id = attrs["attribute"]
        value = attrs["value"]

        if VariantValue.objects.filter(
            attribute_id=attribute_id,
            value__iexact=value,
        ).exists():
            raise serializers.ValidationError({
                "value": "This value already exists for this attribute."
            })

        return attrs


class VariantValueResponseSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField()

    class Meta:
        model = VariantValue
        fields = [
            "id",
            "attribute",
            "value",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_attribute(self, obj):
        return {
            "id": str(obj.attribute.id),
            "name": obj.attribute.name,
            "code": obj.attribute.code,
        }