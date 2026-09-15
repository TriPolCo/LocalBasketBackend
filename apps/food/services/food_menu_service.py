from django.db.models import Prefetch
from django.core.exceptions import ValidationError

from apps.food.models.menu_category import MenuCategory
from apps.food.models.food_item import FoodItem
from apps.food.models.food_item_variant import FoodItemVariant
from apps.food.models.food_item_addon import FoodItemAddon


class FoodMenuService:

    @staticmethod
    def get_categories():
        return (
            MenuCategory.objects
            .filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "food_items",
                    queryset=FoodItem.objects.filter(
                        is_active=True,
                        is_available=True,
                    )
                    .select_related("category")
                    .prefetch_related(
                        Prefetch(
                            "variants",
                            queryset=FoodItemVariant.objects.filter(
                                is_available=True,
                            ),
                        ),
                        Prefetch(
                            "addons",
                            queryset=FoodItemAddon.objects.filter(
                                is_available=True,
                            ),
                        ),
                    ),
                )
            )
            .order_by("display_order", "created_at")
        )

    @staticmethod
    def get_category(category_id):
        try:
            return (
                MenuCategory.objects
                .filter(
                    id=category_id,
                    is_active=True,
                )
                .prefetch_related(
                    Prefetch(
                        "food_items",
                        queryset=FoodItem.objects.filter(
                            is_active=True,
                            is_available=True,
                        )
                        .select_related("category")
                        .prefetch_related(
                            Prefetch(
                                "variants",
                                queryset=FoodItemVariant.objects.filter(
                                    is_available=True,
                                ),
                            ),
                            Prefetch(
                                "addons",
                                queryset=FoodItemAddon.objects.filter(
                                    is_available=True,
                                ),
                            ),
                        ),
                    )
                )
                .get()
            )
        except MenuCategory.DoesNotExist:
            raise ValidationError({
                "category": "Food category not found."
            })

    @staticmethod
    def get_food_items(params=None):
        params = params or {}

        queryset = (
            FoodItem.objects
            .filter(
                is_active=True,
                is_available=True,
                category__is_active=True,
            )
            .select_related("category")
            .prefetch_related(
                Prefetch(
                    "variants",
                    queryset=FoodItemVariant.objects.filter(
                        is_available=True,
                    ),
                ),
                Prefetch(
                    "addons",
                    queryset=FoodItemAddon.objects.filter(
                        is_available=True,
                    ),
                ),
            )
        )

        category = params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        food_type = params.get("food_type")
        if food_type:
            queryset = queryset.filter(food_type=food_type)

        bestseller = params.get("is_bestseller")
        if bestseller is not None:
            queryset = queryset.filter(
                is_bestseller=bestseller
            )

        recommended = params.get("is_recommended")
        if recommended is not None:
            queryset = queryset.filter(
                is_recommended=recommended
            )

        search = params.get("search")
        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        return queryset.order_by(
            "display_order",
            "-created_at",
        )

    @staticmethod
    def get_food_item(food_item_id):
        try:
            return (
                FoodItem.objects
                .filter(
                    id=food_item_id,
                    is_active=True,
                    is_available=True,
                    category__is_active=True,
                )
                .select_related("category")
                .prefetch_related(
                    Prefetch(
                        "variants",
                        queryset=FoodItemVariant.objects.filter(
                            is_available=True,
                        ),
                    ),
                    Prefetch(
                        "addons",
                        queryset=FoodItemAddon.objects.filter(
                            is_available=True,
                        ),
                    ),
                )
                .get()
            )
        except FoodItem.DoesNotExist:
            raise ValidationError({
                "food_item": "Food item not found."
            })