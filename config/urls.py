from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/categories/", include("apps.categories.urls")),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/v1/brands/",include("apps.brands.urls"),),
    path("api/v1/notifications/",include("apps.notifications.urls"),),
    path("api/v1/cart/",include("apps.cart.urls"),),
    path("api/v1/address/",include("apps.address.urls"),),
    path("api/v1/orders/",include("apps.orders.urls"),),
    path("api/v1/printing/",include("apps.printing.urls"),),
    path("api/v1/food/",include("apps.food.urls"),),

]