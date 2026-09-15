from django.urls import path

from apps.products.views.product_view import create_product,get_products,get_product_by_id
from apps.products.views.variant_attribute_view import create_variant_attribute,get_variant_attributes
from apps.products.views.variant_value_view import create_variant_value

urlpatterns = [
    path("",get_products,name="get-products",),
    path("<uuid:product_id>/",get_product_by_id, name="get-product-by-id",),
    path("create/", create_product, name="create-product"),
    path("variant-attributes/create/",create_variant_attribute,name="create-variant-attribute",),
    path("variant-attributes/",get_variant_attributes,name="get-variant-attributes",),
    path("variant-values/create/",create_variant_value,name="create-variant-value",),
]