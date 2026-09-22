from django.db import transaction

from apps.invoices.models.invoice import Invoice
from apps.invoices.utils.qr_service import generate_qr_token


class InvoiceService:

    @staticmethod
    @transaction.atomic
    def get_or_create_invoice(order):

        invoice = Invoice.objects.filter(
            order=order
        ).first()

        if invoice:
            return invoice

        invoice_number = f"INV-{order.order_number}"

        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            order=order,
            qr_token=generate_qr_token(),
        )

        return invoice