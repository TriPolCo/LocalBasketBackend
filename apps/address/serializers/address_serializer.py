from rest_framework import serializers
from apps.address.models.address import Address

class AddressCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            "address_type",
            "full_name",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "landmark",
            "city",
            "state",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_default",
        ]

        extra_kwargs = {
            "address_line_2": {
                "required": False,
                "allow_blank": True,
            },
            "landmark": {
                "required": False,
                "allow_blank": True,
            },
            "country": {
                "required": False,
            },
            "latitude": {
                "required": False,
            },
            "longitude": {
                "required": False,
            },
            "is_default": {
                "required": False,
            },
        }

    def validate_phone_number(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only numbers."
            )

        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10 and 15 digits."
            )

        return value

    def validate_postal_code(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Postal code must contain only numbers."
            )

        return value


class AddressUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            "address_type",
            "full_name",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "landmark",
            "city",
            "state",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_default",
        ]

        extra_kwargs = {
            field: {
                "required": False,
            }
            for field in [
                "address_type",
                "full_name",
                "phone_number",
                "address_line_1",
                "address_line_2",
                "landmark",
                "city",
                "state",
                "postal_code",
                "country",
                "latitude",
                "longitude",
                "is_default",
            ]
        }

    def validate_phone_number(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only numbers."
            )

        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10 and 15 digits."
            )

        return value

    def validate_postal_code(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Postal code must contain only numbers."
            )

        return value


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            "id",
            "address_type",
            "full_name",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "landmark",
            "city",
            "state",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]