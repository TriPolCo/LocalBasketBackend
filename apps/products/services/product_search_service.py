from django.db.models import Q

from apps.products.models.product import Product


class ProductSearchService:

    @staticmethod
    def search_products(search):
        search = search.strip()

        if not search:
            return Product.objects.none()

        products = (
            Product.objects
            .filter(is_active=True)
            .filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(slug__icontains=search)
                | Q(variants__sku__icontains=search)
                | Q(category__name__icontains=search)
                | Q(subcategory__name__icontains=search)
                | Q(brand__name__icontains=search)
                | Q(
                    variants__variant_values__value__value__icontains=search
                )
                | Q(
                    variants__variant_values__value__attribute__name__icontains=search
                )
            )
            .select_related(
                "category",
                "subcategory",
            )
            .prefetch_related(
                "variants__images",
            )
            .distinct()
            .order_by("name")
        )

        return products