from django.urls import path

from apps.food.views.admin_food_view import (
    admin_get_menu_categories,
    admin_create_menu_category,
    admin_get_menu_category,
    admin_update_menu_category,
    admin_delete_menu_category,

    admin_get_food_items,
    admin_create_food_item,
    admin_get_food_item,
    admin_update_food_item,
    admin_delete_food_item,
)

from apps.food.views.food_setting_view import (
    get_food_store_status,
    admin_update_food_store_status,
)
from apps.food.views.food_menu_view import get_food_menus, get_food_items_by_menu
from apps.food.views.food_cart_view import get_food_cart, add_food_to_cart, update_food_cart_item, \
    increase_food_cart_item, \
    decrease_food_cart_item, remove_food_cart_item, clear_food_cart
from apps.food.views.food_order_view import place_food_order, get_food_orders, get_food_order, cancel_food_order
from apps.food.views.admin_food_order_view import admin_get_food_orders, admin_get_food_order, \
    admin_update_food_order_status, admin_assign_food_delivery, admin_update_food_delivery_fee

urlpatterns = [
    path("admin/menu/categories/",admin_get_menu_categories,name="admin-food-menu-categories",),
    path("admin/menu/categories/create/",admin_create_menu_category,name="admin-create-food-menu-category",),
    path("admin/menu/categories/<uuid:category_id>/",admin_get_menu_category,name="admin-food-menu-category",),
    path("admin/menu/categories/<uuid:category_id>/update/",admin_update_menu_category,name="admin-update-food-menu-category",),
    path("admin/menu/categories/<uuid:category_id>/delete/",admin_delete_menu_category,name="admin-delete-food-menu-category",),

    # FOOD ITEMS
    path("admin/menu/items/",admin_get_food_items,name="admin-food-items",),
    path("admin/menu/items/create/",admin_create_food_item,name="admin-create-food-item",),
    path("admin/menu/items/<uuid:food_item_id>/",admin_get_food_item,name="admin-food-item",),
    path("admin/menu/items/<uuid:food_item_id>/update/",admin_update_food_item,name="admin-update-food-item",),
    path("admin/menu/items/<uuid:food_item_id>/delete/",admin_delete_food_item,name="admin-delete-food-item",),

    #User APIS
    path("menus/",get_food_menus,name="food-menus",),
    path("menus/<uuid:menu_id>/items/",get_food_items_by_menu,name="food-items-by-menu",),

    #Cart APIS
    path("cart/",get_food_cart,name="food-cart",),
    path("cart/add/",add_food_to_cart,name="add-food-to-cart",),
    path("cart/<uuid:item_id>/",update_food_cart_item, name="update-food-cart-item",),
    path("cart/<uuid:item_id>/increase/",increase_food_cart_item,name="increase-food-cart-item",),
    path("cart/<uuid:item_id>/decrease/",decrease_food_cart_item,name="decrease-food-cart-item",),
    path("cart/<uuid:item_id>/remove/",remove_food_cart_item,name="remove-food-cart-item",),
    path("cart/clear/",clear_food_cart,name="clear-food-cart",),


    #Order APIS
    path("orders/place/",place_food_order,name="place-food-order",),
    path("orders/",get_food_orders,name="food-orders",),
    path("orders/<uuid:order_id>/",get_food_order, name="food-order-detail",),
    path("orders/<uuid:order_id>/cancel/",cancel_food_order,name="cancel-food-order",),



    path("admin/orders/",admin_get_food_orders,name="admin-food-orders",),
    path("admin/orders/<uuid:order_id>/",admin_get_food_order,name="admin-food-order-detail",),
    path("admin/orders/<uuid:order_id>/status/",admin_update_food_order_status,name="admin-update-food-order-status",),
    path("admin/orders/<uuid:order_id>/assign-delivery/",admin_assign_food_delivery,name="admin-assign-food-delivery",),
    path("admin/orders/<uuid:order_id>/delivery-fee/",admin_update_food_delivery_fee, name="admin-update-food-delivery-fee",
),


    path("store-status/", get_food_store_status, name="food-store-status"),
    path("admin/store-status/", admin_update_food_store_status, name="admin-food-store-status"),
]