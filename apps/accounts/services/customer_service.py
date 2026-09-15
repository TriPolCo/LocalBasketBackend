from django.db import transaction

from apps.accounts.models.customer import Customer


class CustomerService:

    @staticmethod
    @transaction.atomic
    def create_customer(user):
        customer = Customer.objects.create(
            user=user,
            is_verified=False,
        )

        return customer