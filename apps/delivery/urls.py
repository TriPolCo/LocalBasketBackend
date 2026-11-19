from django.urls import path

from apps.delivery.views.delivery_assignment_view import (
    accept_delivery_assignment,
    assign_delivery_order,
    complete_delivery_assignment,
    get_delivery_assignment,
    get_delivery_assignments,
    get_my_delivery_assignments,
    scan_delivery_assignment,
    start_delivery_assignment,
    upload_delivery_proof,
)


urlpatterns = [
    # Admin
    path(
        "assign/",
        assign_delivery_order,
        name="assign-delivery-order",
    ),
    path(
        "assignments/",
        get_delivery_assignments,
        name="delivery-assignments",
    ),

    # Delivery Partner
    path(
        "my-assignments/",
        get_my_delivery_assignments,
        name="my-delivery-assignments",
    ),
    path(
        "my-assignments/scan/<str:code>/",
        scan_delivery_assignment,
        name="scan-delivery-assignment",
    ),
    path(
        "assignments/<uuid:assignment_id>/",
        get_delivery_assignment,
        name="delivery-assignment-detail",
    ),
    path(
        "assignments/<uuid:assignment_id>/accept/",
        accept_delivery_assignment,
        name="accept-delivery-assignment",
    ),
    path(
        "assignments/<uuid:assignment_id>/start/",
        start_delivery_assignment,
        name="start-delivery-assignment",
    ),
    path(
        "assignments/<uuid:assignment_id>/complete/",
        complete_delivery_assignment,
        name="complete-delivery-assignment",
    ),
    path(
        "assignments/<uuid:assignment_id>/proof/",
        upload_delivery_proof,
        name="upload-delivery-proof",
    ),
]