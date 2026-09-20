from django.db.models import F, ExpressionWrapper, DecimalField

from apps.products.models.variant import ProductVariant


class FlashSaleService:

    @staticmethod
    def get_flash_sale_products():

        variants = (
            ProductVariant.objects
            .filter(
                is_active=True,
                product__is_active=True,
                mrp__gt=0,
                selling_price__lt=F("mrp"),
            )
            .annotate(
                discount_percentage=ExpressionWrapper(
                    (
                        (F("mrp") - F("selling_price"))
                        * 100
                        / F("mrp")
                    ),
                    output_field=DecimalField(
                        max_digits=5,
                        decimal_places=2
                    )
                )
            )
            .filter(
                discount_percentage__gte=15
            )
            .select_related(
                "product",
                "product__category",
                "product__subcategory",
            )
            .prefetch_related(
                "images"
            )
            .order_by(
                "-discount_percentage"
            )
        )

        return variants