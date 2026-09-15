import random
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.printing.models.printing_service import PrintingService
from apps.printing.models.print_pricing import PrintPricing
from apps.printing.models.print_order import PrintOrder
from apps.printing.models.print_document import PrintDocument


class PrintOrderService:

    @staticmethod
    def generate_order_number():

        while True:

            number = (
                f"LBP-"
                f"{timezone.now().strftime('%Y%m%d')}-"
                f"{random.randint(10000, 99999)}"
            )

            if not PrintOrder.objects.filter(
                order_number=number
            ).exists():

                return number

    @staticmethod
    def calculate_document_pages(
        page_count,
        page_start,
        page_end,
    ):

        if page_start is None and page_end is None:
            return page_count

        if page_start is None or page_end is None:
            raise ValidationError(
                "Both page_start and page_end are required."
            )

        if page_start > page_end:
            raise ValidationError(
                "page_start cannot be greater than page_end."
            )

        if page_end > page_count:
            raise ValidationError(
                "page_end cannot be greater than page_count."
            )

        return page_end - page_start + 1

    @staticmethod
    def get_pricing(
        service,
        color_type,
        paper_size,
        print_side,
    ):

        pricing = (
            PrintPricing.objects
            .filter(
                service=service,
                color_type=color_type,
                paper_size=paper_size,
                print_side=print_side,
                is_active=True,
            )
            .first()
        )

        if not pricing:
            raise ValidationError(
                {
                    "pricing": (
                        "No active pricing found for "
                        f"{service.name}, "
                        f"{paper_size}, "
                        f"{color_type}, "
                        f"{print_side}."
                    )
                }
            )

        return pricing

    @staticmethod
    @transaction.atomic
    def create_print_order(
        customer,
        documents,
        notes=None,
    ):

        if not documents:
            raise ValidationError(
                "At least one document is required."
            )

        subtotal = Decimal("0.00")

        prepared_documents = []

        for document_data in documents:

            service_id = document_data["service"]

            try:
                service = PrintingService.objects.get(
                    id=service_id,
                    is_active=True,
                )
            except PrintingService.DoesNotExist:
                raise ValidationError(
                    "Printing service not found or inactive."
                )

            page_count = document_data["page_count"]

            page_start = document_data.get("page_start")
            page_end = document_data.get("page_end")

            selected_pages = (
                PrintOrderService.calculate_document_pages(
                    page_count=page_count,
                    page_start=page_start,
                    page_end=page_end,
                )
            )

            copies = document_data["copies"]

            color_type = document_data["color_type"]
            paper_size = document_data["paper_size"]
            print_side = document_data["print_side"]

            pricing = PrintOrderService.get_pricing(
                service=service,
                color_type=color_type,
                paper_size=paper_size,
                print_side=print_side,
            )

            printable_pages = selected_pages * copies

            amount = (
                Decimal(printable_pages)
                * pricing.price_per_page
            )

            if (
                pricing.minimum_charge > 0
                and amount < pricing.minimum_charge
            ):
                amount = pricing.minimum_charge

            subtotal += amount

            prepared_documents.append(
                {
                    "service": service,
                    "data": document_data,
                    "price_per_page": pricing.price_per_page,
                    "total_amount": amount,
                }
            )

        delivery_fee = Decimal("0.00")
        discount = Decimal("0.00")

        total_amount = (
            subtotal
            + delivery_fee
            - discount
        )

        order = PrintOrder.objects.create(
            order_number=PrintOrderService.generate_order_number(),
            customer=customer,
            status=PrintOrder.Status.PENDING,
            payment_method="COD",
            payment_status=PrintOrder.PaymentStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            total_amount=total_amount,
            notes=notes,
        )

        for index, prepared in enumerate(
            prepared_documents
        ):

            data = prepared["data"]

            PrintDocument.objects.create(
                print_order=order,
                service=prepared["service"],
                file_name=data["file_name"],
                file_url=data["file_url"],
                cloudinary_public_id=data.get(
                    "cloudinary_public_id"
                ),
                file_type=data.get("file_type"),
                file_size=data.get("file_size"),
                page_count=data["page_count"],
                color_type=data["color_type"],
                paper_size=data["paper_size"],
                print_side=data["print_side"],
                copies=data["copies"],
                page_start=data.get("page_start"),
                page_end=data.get("page_end"),
                price_per_page=prepared["price_per_page"],
                total_amount=prepared["total_amount"],
                display_order=index,
            )

        return order

    @staticmethod
    def get_customer_orders(customer):

        return (
            PrintOrder.objects
            .filter(customer=customer)
            .prefetch_related(
                "documents",
                "documents__service",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_customer_order(
        customer,
        order_id,
    ):

        try:
            return (
                PrintOrder.objects
                .select_related("customer")
                .prefetch_related(
                    "documents",
                    "documents__service",
                )
                .get(
                    id=order_id,
                    customer=customer,
                )
            )

        except PrintOrder.DoesNotExist:
            raise ValidationError(
                "Print order not found."
            )

    @staticmethod
    @transaction.atomic
    def cancel_order(
        customer,
        order_id,
    ):

        try:
            order = (
                PrintOrder.objects
                .select_for_update()
                .get(
                    id=order_id,
                    customer=customer,
                )
            )

        except PrintOrder.DoesNotExist:
            raise ValidationError(
                "Print order not found."
            )

        if order.status not in [
            PrintOrder.Status.PENDING,
            PrintOrder.Status.CONFIRMED,
        ]:
            raise ValidationError(
                "This print order cannot be cancelled."
            )

        order.status = PrintOrder.Status.CANCELLED
        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order

    @staticmethod
    def get_all_orders():

        return (
            PrintOrder.objects
            .select_related(
                "customer",
                "customer__user",
            )
            .prefetch_related(
                "documents",
                "documents__service",
            )
            .order_by("-created_at")
        )

    @staticmethod
    @transaction.atomic
    def update_order_status(
        order_id,
        new_status,
    ):

        try:
            order = (
                PrintOrder.objects
                .select_for_update()
                .get(id=order_id)
            )

        except PrintOrder.DoesNotExist:
            raise ValidationError(
                "Print order not found."
            )

        current_status = order.status

        allowed_transitions = {
            PrintOrder.Status.PENDING: [
                PrintOrder.Status.CONFIRMED,
                PrintOrder.Status.CANCELLED,
            ],
            PrintOrder.Status.CONFIRMED: [
                PrintOrder.Status.PROCESSING,
                PrintOrder.Status.CANCELLED,
            ],
            PrintOrder.Status.PROCESSING: [
                PrintOrder.Status.READY,
            ],
            PrintOrder.Status.READY: [
                PrintOrder.Status.COMPLETED,
            ],
            PrintOrder.Status.COMPLETED: [],
            PrintOrder.Status.CANCELLED: [],
        }

        if new_status not in allowed_transitions.get(
            current_status,
            [],
        ):
            raise ValidationError(
                f"Cannot change status from "
                f"{current_status} to {new_status}."
            )

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order