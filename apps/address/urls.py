from django.urls import path

from apps.address.views.address_view import (
    create_address,
    get_addresses,
    get_address,
    update_address,
    set_default_address,
    delete_address,
)


urlpatterns = [
    path(
        "",
        get_addresses,
        name="get-addresses",
    ),

    path(
        "create/",
        create_address,
        name="create-address",
    ),

    path(
        "<uuid:address_id>/",
        get_address,
        name="get-address",
    ),

    path(
        "<uuid:address_id>/update/",
        update_address,
        name="update-address",
    ),

    path(
        "<uuid:address_id>/set-default/",
        set_default_address,
        name="set-default-address",
    ),

    path(
        "<uuid:address_id>/delete/",
        delete_address,
        name="delete-address",
    ),
]