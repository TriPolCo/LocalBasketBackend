from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.invoices.models.invoice import Invoice
from apps.invoices.services.invoice_service import InvoiceService
from apps.invoices.services.pdf_service import InvoicePDFService
from apps.orders.models.order import Order


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_invoice(request, order_id):

    # ---------------------------------------------------------
    # ADMIN CHECK
    # ---------------------------------------------------------

    if (
        request.user.role != "ADMIN"
        or not request.user.is_staff
    ):
        return Response(
            {
                "success": False,
                "message": "Only admin can download parcel labels.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # GET ORDER
    # ---------------------------------------------------------

    try:
        order = (
            Order.objects
            .prefetch_related("items")
            .get(id=order_id)
        )

    except Order.DoesNotExist:

        return Response(
            {
                "success": False,
                "message": "Order not found.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # ---------------------------------------------------------
    # GET / CREATE INVOICE
    # ---------------------------------------------------------

    invoice = InvoiceService.get_or_create_invoice(
        order
    )

    # ---------------------------------------------------------
    # GENERATE PDF
    # ---------------------------------------------------------

    pdf_buffer = InvoicePDFService.generate(
        invoice
    )

    filename = (
        f"DailyDrops-"
        f"{order.order_number}-"
        f"Label.pdf"
    )

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def verify_delivery_qr(request, token):

    # ---------------------------------------------------------
    # IMPORTANT:
    # NO ORDER DATA IS RETURNED BEFORE AUTHORIZATION
    # ---------------------------------------------------------

    if not request.user.is_authenticated:

        return Response(
            {
                "success": False,
                "message": (
                    "This QR code is only available "
                    "for delivery partners."
                ),
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # ROLE CHECK
    # ---------------------------------------------------------

    if request.user.role != "DELIVERY_PARTNER":

        return Response(
            {
                "success": False,
                "message": (
                    "This QR code is only available "
                    "for delivery partners."
                ),
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # FIND INVOICE
    # ---------------------------------------------------------

    try:

        invoice = (
            Invoice.objects
            .select_related("order")
            .prefetch_related("order__items")
            .get(qr_token=token)
        )

    except Invoice.DoesNotExist:

        return Response(
            {
                "success": False,
                "message": "Invalid or expired QR code.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    order = invoice.order

    # ---------------------------------------------------------
    # OPTIONAL STATUS CHECK
    # ---------------------------------------------------------

    if order.status == Order.Status.CANCELLED:

        return Response(
            {
                "success": False,
                "message": "This order has been cancelled.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # AMOUNT TO COLLECT
    # ---------------------------------------------------------

    amount_to_collect = (
        order.total_amount
        if order.payment_status != "PAID"
        else 0
    )

    items = []

    for item in order.items.all():

        items.append(
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "selling_price": item.selling_price,
                "item_total": item.item_total,
            }
        )

    # ---------------------------------------------------------
    # RETURN DELIVERY DATA
    # ---------------------------------------------------------

    return Response(
        {
            "success": True,
            "message": "Delivery order verified.",
            "data": {
                "invoice_number": invoice.invoice_number,
                "order_number": order.order_number,

                "customer": {
                    "name": order.shipping_full_name,
                    "phone": order.shipping_phone_number,
                },

                "address": {
                    "line_1": order.shipping_address_line_1,
                    "line_2": order.shipping_address_line_2,
                    "landmark": order.shipping_landmark,
                    "city": order.shipping_city,
                    "state": order.shipping_state,
                    "postal_code": order.shipping_postal_code,
                    "country": order.shipping_country,
                },

                "items": items,

                "payment": {
                    "method": order.payment_method,
                    "status": order.payment_status,
                    "total_amount": order.total_amount,
                    "amount_to_collect": amount_to_collect,
                },

                "order_status": order.status,
            },
        },
        status=status.HTTP_200_OK,
    )