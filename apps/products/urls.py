# apps/products/urls.py
from django.urls import path

from apps.products.views.flash_sale_view import get_flash_sale_products
from apps.products.views.product_search_view import search_products
from apps.products.views.product_view import (
    create_product,
    get_popular_products,
    get_product_by_id,
    get_products,
    get_products_by_category,
    toggle_product_status,
      get_products_admin  # 👈 Added here
)
from apps.products.views.variant_attribute_view import (
    create_variant_attribute,
    get_variant_attributes,
)
from apps.products.views.variant_price_view import update_variant_price
from apps.products.views.variant_value_view import create_variant_value

urlpatterns = [
    path("", get_products, name="get-products"),
    path("admin/", get_products_admin, name="get-products"),

    path("create/", create_product, name="create-product"),

    # ⚡ Toggle / Set Product Active/Inactive Status
    path("<uuid:product_id>/status/", toggle_product_status, name="toggle-product-status"),
    path("<uuid:product_id>/toggle-status/", toggle_product_status, name="toggle-product-status-alias"),

    path("variants/<uuid:variant_id>/", update_variant_price, name="update-variant-price"),
    path("variant-attributes/create/", create_variant_attribute, name="create-variant-attribute"),
    path("variant-attributes/", get_variant_attributes, name="get-variant-attributes"),
    path("variant-values/create/", create_variant_value, name="create-variant-value"),
    path("search/", search_products, name="search-products"),
    path("flash-sale/", get_flash_sale_products, name="flash-sale-products"),
    path("category/<uuid:category_id>/", get_products_by_category, name="products-by-category"),
    path("popular/", get_popular_products, name="popular-products"),
    path("<uuid:product_id>/", get_product_by_id, name="get-product-by-id"),
]