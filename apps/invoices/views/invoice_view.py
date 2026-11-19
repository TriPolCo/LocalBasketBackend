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

    invoice = InvoiceService.get_or_create_invoice(order)

    # ---------------------------------------------------------
    # GENERATE PDF
    # ---------------------------------------------------------

    pdf_buffer = InvoicePDFService.generate(invoice)

    filename = f"DailyDrops-{order.order_number}-Label.pdf"

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
    # AUTHORIZATION & ROLE CHECK
    # ---------------------------------------------------------

    if not request.user.is_authenticated:
        return Response(
            {
                "success": False,
                "message": "This QR code is only available for delivery partners.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.user.role != "DELIVERY_PARTNER":
        return Response(
            {
                "success": False,
                "message": "This QR code is only available for delivery partners.",
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
            .select_related("order", "order__delivery_assignment")
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
    # STATUS CHECK
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

    items = [
        {
            "product_name": item.product_name,
            "quantity": item.quantity,
            "selling_price": float(item.selling_price),
            "item_total": float(item.item_total),
        }
        for item in order.items.all()
    ]

    manual_items = getattr(order, "manual_items", None) or []

    # ---------------------------------------------------------
    # LINKED DELIVERY ASSIGNMENT
    # ---------------------------------------------------------

    try:
        assignment = order.delivery_assignment
    except Exception:
        assignment = None

    partner_profile = getattr(request.user, "delivery_partner_profile", None)
    assigned_to_me = bool(
        assignment
        and partner_profile
        and str(assignment.delivery_partner_id) == str(partner_profile.id)
    )

    # ---------------------------------------------------------
    # RETURN VERIFIED DELIVERY DATA
    # ---------------------------------------------------------

    return Response(
        {
            "success": True,
            "message": "Delivery order verified.",
            "data": {
                "order_id": str(order.id),
                "assignment_id": str(assignment.id) if assignment else None,
                "assignment_status": assignment.status if assignment else None,
                "assigned_to_me": assigned_to_me,
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
                "manual_items": manual_items,
                "payment": {
                    "method": order.payment_method,
                    "status": order.payment_status,
                    "total_amount": float(order.total_amount),
                    "amount_to_collect": float(amount_to_collect),
                },
                "order_status": order.status,
            },
        },
        status=status.HTTP_200_OK,
    )