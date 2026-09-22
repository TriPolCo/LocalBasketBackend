from django.urls import path

from apps.invoices.views.invoice_view import (
    download_invoice,
    verify_delivery_qr,
)


urlpatterns = [

    # Admin
    path("admin/orders/<uuid:order_id>/download/",download_invoice,name="admin-download-invoice",),

    # Delivery Partner
    path("delivery/verify/<str:token>/",verify_delivery_qr,name="verify-delivery-qr",),
]