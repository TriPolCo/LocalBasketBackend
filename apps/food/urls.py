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


urlpatterns = [
    path("admin/menu/categories/",
        admin_get_menu_categories,
        name="admin-food-menu-categories",
    ),

    path(
        "admin/menu/categories/create/",
        admin_create_menu_category,
        name="admin-create-food-menu-category",
    ),

    path(
        "admin/menu/categories/<uuid:category_id>/",
        admin_get_menu_category,
        name="admin-food-menu-category",
    ),

    path(
        "admin/menu/categories/<uuid:category_id>/update/",
        admin_update_menu_category,
        name="admin-update-food-menu-category",
    ),

    path(
        "admin/menu/categories/<uuid:category_id>/delete/",
        admin_delete_menu_category,
        name="admin-delete-food-menu-category",
    ),

    # ==========================================================
    # FOOD ITEMS
    # ==========================================================

    path(
        "admin/menu/items/",
        admin_get_food_items,
        name="admin-food-items",
    ),

    path(
        "admin/menu/items/create/",
        admin_create_food_item,
        name="admin-create-food-item",
    ),

    path(
        "admin/menu/items/<uuid:food_item_id>/",
        admin_get_food_item,
        name="admin-food-item",
    ),

    path(
        "admin/menu/items/<uuid:food_item_id>/update/",
        admin_update_food_item,
        name="admin-update-food-item",
    ),

    path(
        "admin/menu/items/<uuid:food_item_id>/delete/",
        admin_delete_food_item,
        name="admin-delete-food-item",
    ),
]