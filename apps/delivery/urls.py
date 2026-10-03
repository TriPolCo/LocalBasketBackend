from django.urls import path

from apps.delivery.views.delivery_assignment_view import (
    assign_delivery_order,
    get_delivery_assignments,
    get_delivery_assignment, upload_delivery_proof, get_all_assignments,
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

    path(
        "assignments/<uuid:assignment_id>/",
        get_delivery_assignment,
        name="delivery-assignment-detail",
    ),

    path(
        "assignments/<uuid:assignment_id>/proof/",
        upload_delivery_proof,
        name="upload-delivery-proof",
    ),

path(
    "assignments/",
    get_all_assignments,
    name="get-all-assignments",
),
]