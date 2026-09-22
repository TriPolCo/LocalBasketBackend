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
from apps.food.views.food_menu_view import get_food_menus, get_food_items_by_menu
from apps.food.views.food_cart_view import get_food_cart, add_food_to_cart, update_food_cart_item, \
    increase_food_cart_item, \
    decrease_food_cart_item, remove_food_cart_item, clear_food_cart

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
]