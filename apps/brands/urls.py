from django.urls import path

from apps.brands.views.brand_view import create_brand


urlpatterns = [
    path("create/",create_brand,name="create-brand",),
]