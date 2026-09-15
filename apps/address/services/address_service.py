from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.address.models.address import Address


class AddressService:

    @staticmethod
    def get_addresses(customer):
        return Address.objects.filter(
            customer=customer
        ).order_by(
            "-is_default",
            "-created_at",
        )

    @staticmethod
    def get_address(customer, address_id):
        address = Address.objects.filter(
            id=address_id,
            customer=customer,
        ).first()

        if not address:
            raise ValidationError("Address not found.")

        return address

    @staticmethod
    @transaction.atomic
    def create_address(customer, **validated_data):

        is_default = validated_data.pop(
            "is_default",
            False,
        )

        has_existing_address = Address.objects.filter(
            customer=customer
        ).exists()

        # First address automatically becomes default
        if not has_existing_address:
            is_default = True

        if is_default:
            Address.objects.filter(
                customer=customer,
                is_default=True,
            ).update(
                is_default=False
            )

        address = Address.objects.create(
            customer=customer,
            is_default=is_default,
            **validated_data,
        )

        return address

    @staticmethod
    @transaction.atomic
    def update_address(
        customer,
        address_id,
        **validated_data,
    ):

        address = (
            Address.objects
            .select_for_update()
            .filter(
                id=address_id,
                customer=customer,
            )
            .first()
        )

        if not address:
            raise ValidationError("Address not found.")

        is_default = validated_data.pop(
            "is_default",
            None,
        )

        # User explicitly wants this address to be default
        if is_default is True:

            Address.objects.filter(
                customer=customer,
                is_default=True,
            ).exclude(
                id=address.id
            ).update(
                is_default=False
            )

            address.is_default = True

        # User explicitly wants this address NOT to be default
        elif is_default is False:

            # Don't allow customer to end up with
            # zero default addresses when others exist.
            if address.is_default:

                other_address = (
                    Address.objects
                    .filter(
                        customer=customer
                    )
                    .exclude(
                        id=address.id
                    )
                    .order_by("-created_at")
                    .first()
                )

                if other_address:
                    other_address.is_default = True
                    other_address.save(
                        update_fields=[
                            "is_default",
                            "updated_at",
                        ]
                    )

                address.is_default = False

        for field, value in validated_data.items():
            setattr(address, field, value)

        address.save()

        return address

    @staticmethod
    @transaction.atomic
    def set_default_address(
        customer,
        address_id,
    ):

        address = (
            Address.objects
            .select_for_update()
            .filter(
                id=address_id,
                customer=customer,
            )
            .first()
        )

        if not address:
            raise ValidationError("Address not found.")

        # Remove existing default
        Address.objects.filter(
            customer=customer,
            is_default=True,
        ).exclude(
            id=address.id
        ).update(
            is_default=False
        )

        address.is_default = True

        address.save(
            update_fields=[
                "is_default",
                "updated_at",
            ]
        )

        return address

    @staticmethod
    @transaction.atomic
    def delete_address(
        customer,
        address_id,
    ):

        address = (
            Address.objects
            .select_for_update()
            .filter(
                id=address_id,
                customer=customer,
            )
            .first()
        )

        if not address:
            raise ValidationError("Address not found.")

        was_default = address.is_default

        address.delete()

        # If deleted address was default,
        # promote another address.
        if was_default:

            new_default = (
                Address.objects
                .filter(customer=customer)
                .order_by("-created_at")
                .first()
            )

            if new_default:
                new_default.is_default = True

                new_default.save(
                    update_fields=[
                        "is_default",
                        "updated_at",
                    ]
                )