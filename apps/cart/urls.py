from django.urls import path

from apps.cart.views.cart_view import (
    get_cart,
    add_to_cart,
    update_cart_quantity,
    increase_cart_quantity,
    decrease_cart_quantity,
    remove_cart_item,
    clear_cart,
)


urlpatterns = [

    # Get cart
    path(
        "",
        get_cart,
        name="get-cart",
    ),

    # Add item
    path(
        "add/",
        add_to_cart,
        name="add-to-cart",
    ),

    # Set quantity
    path(
        "items/<uuid:item_id>/quantity/",
        update_cart_quantity,
        name="update-cart-quantity",
    ),

    # Increase
    path(
        "items/<uuid:item_id>/increase/",
        increase_cart_quantity,
        name="increase-cart-quantity",
    ),

    # Decrease
    path(
        "items/<uuid:item_id>/decrease/",
        decrease_cart_quantity,
        name="decrease-cart-quantity",
    ),

    # Remove
    path(
        "items/<uuid:item_id>/",
        remove_cart_item,
        name="remove-cart-item",
    ),

    # Clear
    path(
        "clear/",
        clear_cart,
        name="clear-cart",
    ),
]