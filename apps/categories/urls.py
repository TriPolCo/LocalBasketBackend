from django.urls import path

from apps.categories.views.category_views import (category_list,category_tree,category_detail,create_category,
    update_category,delete_category_view,create_subcategory_view,subcategory_list,update_subcategory_view,delete_subcategory_view,)


urlpatterns = [
    path("",category_list, name="category-list",),
    path("tree/",category_tree,name="category-tree",),
    path("create/",create_category,name="category-create",),
    path("<uuid:category_id>/",category_detail,name="category-detail",),
    path("<uuid:category_id>/update/",update_category,name="category-update",),
    path("<uuid:category_id>/delete/",delete_category_view,name="category-delete",),
    path("<uuid:category_id>/subcategories/",subcategory_list,name="subcategory-list",),
    path("<uuid:category_id>/subcategories/create/",create_subcategory_view,name="subcategory-create",),
    path("subcategories/<uuid:subcategory_id>/update/",update_subcategory_view, name="subcategory-update",),
    path("subcategories/<uuid:subcategory_id>/delete/",delete_subcategory_view,name="subcategory-delete",),
]