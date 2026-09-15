from django.db import transaction
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.food.models.menu_category import MenuCategory
from apps.food.models.food_item import FoodItem
from apps.food.models.food_item_variant import FoodItemVariant
from apps.food.models.food_item_addon import FoodItemAddon


class MenuService:
    @staticmethod
    @transaction.atomic
    def create_category(**data):

        name = data["name"].strip()

        if MenuCategory.objects.filter(
            name__iexact=name
        ).exists():
            raise ValidationError(
                {
                    "name": "Menu category already exists."
                }
            )

        slug = slugify(name)

        category = MenuCategory.objects.create(
            name=name,
            slug=slug,
            description=data.get("description"),
            image_url=data.get("image_url"),
            cloudinary_public_id=data.get(
                "cloudinary_public_id"
            ),
            display_order=data.get(
                "display_order",
                0,
            ),
            is_active=data.get(
                "is_active",
                True,
            ),
        )

        return category

    @staticmethod
    def get_categories():

        return (
            MenuCategory.objects
            .prefetch_related("food_items")
            .order_by(
                "display_order",
                "created_at",
            )
        )

    @staticmethod
    def get_category(category_id):

        try:
            return (
                MenuCategory.objects
                .prefetch_related(
                    "food_items__variants",
                    "food_items__addons",
                )
                .get(id=category_id)
            )

        except MenuCategory.DoesNotExist:
            raise ValidationError({
                "category": "Menu category not found."
            })
    @staticmethod
    @transaction.atomic
    def update_category(
        category_id,
        **data,
    ):

        try:
            category = MenuCategory.objects.get(
                id=category_id
            )

        except MenuCategory.DoesNotExist:
            raise ValidationError(
                "Menu category not found."
            )

        if "name" in data:

            name = data["name"].strip()

            if MenuCategory.objects.filter(
                name__iexact=name
            ).exclude(
                id=category.id
            ).exists():

                raise ValidationError(
                    {
                        "name": (
                            "Another menu category "
                            "with this name already exists."
                        )
                    }
                )

            category.name = name
            category.slug = slugify(name)

        update_fields = []

        for field in [
            "description",
            "image_url",
            "cloudinary_public_id",
            "display_order",
            "is_active",
        ]:

            if field in data:
                setattr(
                    category,
                    field,
                    data[field],
                )
                update_fields.append(field)

        if "name" in data:
            update_fields.extend(
                ["name", "slug"]
            )

        update_fields.append("updated_at")

        category.save(
            update_fields=list(
                set(update_fields)
            )
        )

        return category

    @staticmethod
    @transaction.atomic
    def delete_category(category_id):

        try:
            category = MenuCategory.objects.get(
                id=category_id
            )

        except MenuCategory.DoesNotExist:
            raise ValidationError(
                "Menu category not found."
            )

        if category.food_items.exists():
            raise ValidationError(
                "Cannot delete category containing food items."
            )

        category.delete()

    # ==========================================================
    # FOOD ITEM
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def create_food_item(**data):

        category_id = data["category"]

        try:
            category = MenuCategory.objects.get(
                id=category_id,
                is_active=True,
            )

        except MenuCategory.DoesNotExist:
            raise ValidationError(
                {
                    "category": (
                        "Menu category not found "
                        "or inactive."
                    )
                }
            )

        name = data["name"].strip()

        if FoodItem.objects.filter(
            name__iexact=name
        ).exists():
            raise ValidationError(
                {
                    "name": (
                        "Food item with this name "
                        "already exists."
                    )
                }
            )

        slug = slugify(name)

        variants = data.get(
            "variants",
            [],
        )

        if not variants:
            raise ValidationError(
                {
                    "variants": (
                        "At least one variant "
                        "is required."
                    )
                }
            )

        default_variants = [
            variant
            for variant in variants
            if variant.get("is_default")
        ]

        if len(default_variants) > 1:
            raise ValidationError(
                {
                    "variants": (
                        "Only one variant can "
                        "be default."
                    )
                }
            )

        # If no default was supplied,
        # make the first variant default.
        if not default_variants:
            variants[0]["is_default"] = True

        food_item = FoodItem.objects.create(
            category=category,
            name=name,
            slug=slug,
            description=data.get("description"),
            image_url=data.get("image_url"),
            cloudinary_public_id=data.get(
                "cloudinary_public_id"
            ),
            food_type=data["food_type"],
            is_available=data.get(
                "is_available",
                True,
            ),
            is_active=data.get(
                "is_active",
                True,
            ),
            is_bestseller=data.get(
                "is_bestseller",
                False,
            ),
            is_recommended=data.get(
                "is_recommended",
                False,
            ),
            preparation_time=data.get(
                "preparation_time"
            ),
            display_order=data.get(
                "display_order",
                0,
            ),
        )

        for index, variant_data in enumerate(
            variants
        ):

            FoodItemVariant.objects.create(
                food_item=food_item,
                name=variant_data["name"].strip(),
                price=variant_data["price"],
                is_default=variant_data.get(
                    "is_default",
                    index == 0,
                ),
                is_available=variant_data.get(
                    "is_available",
                    True,
                ),
                display_order=variant_data.get(
                    "display_order",
                    index,
                ),
            )

        for index, addon_data in enumerate(
            data.get("addons", [])
        ):

            FoodItemAddon.objects.create(
                food_item=food_item,
                name=addon_data["name"].strip(),
                price=addon_data["price"],
                is_required=addon_data.get(
                    "is_required",
                    False,
                ),
                max_quantity=addon_data.get(
                    "max_quantity",
                    1,
                ),
                is_available=addon_data.get(
                    "is_available",
                    True,
                ),
                display_order=addon_data.get(
                    "display_order",
                    index,
                ),
            )

        return food_item


    @staticmethod
    @transaction.atomic
    def update_food_item(
        food_item_id,
        **data,
    ):

        try:
            food_item = (
                FoodItem.objects
                .select_for_update()
                .get(id=food_item_id)
            )

        except FoodItem.DoesNotExist:
            raise ValidationError(
                "Food item not found."
            )

        # ------------------------------------------------------
        # CATEGORY
        # ------------------------------------------------------

        if "category" in data:

            try:
                category = MenuCategory.objects.get(
                    id=data["category"],
                    is_active=True,
                )

            except MenuCategory.DoesNotExist:
                raise ValidationError(
                    {
                        "category": (
                            "Menu category not found "
                            "or inactive."
                        )
                    }
                )

            food_item.category = category

        # ------------------------------------------------------
        # NAME
        # ------------------------------------------------------

        if "name" in data:

            name = data["name"].strip()

            if FoodItem.objects.filter(
                name__iexact=name
            ).exclude(
                id=food_item.id
            ).exists():

                raise ValidationError(
                    {
                        "name": (
                            "Another food item "
                            "with this name already exists."
                        )
                    }
                )

            food_item.name = name
            food_item.slug = slugify(name)

        # ------------------------------------------------------
        # SIMPLE FIELDS
        # ------------------------------------------------------

        for field in [
            "description",
            "image_url",
            "cloudinary_public_id",
            "food_type",
            "is_available",
            "is_active",
            "is_bestseller",
            "is_recommended",
            "preparation_time",
            "display_order",
        ]:

            if field in data:
                setattr(
                    food_item,
                    field,
                    data[field],
                )

        food_item.save()

        # ------------------------------------------------------
        # VARIANTS
        # ------------------------------------------------------

        if "variants" in data:

            variants = data["variants"]

            if not variants:
                raise ValidationError(
                    {
                        "variants": (
                            "At least one variant "
                            "is required."
                        )
                    }
                )

            default_count = sum(
                1
                for variant in variants
                if variant.get("is_default")
            )

            if default_count > 1:
                raise ValidationError(
                    {
                        "variants": (
                            "Only one variant "
                            "can be default."
                        )
                    }
                )

            existing_variant_ids = set(
                food_item.variants.values_list(
                    "id",
                    flat=True,
                )
            )

            submitted_variant_ids = set()

            for index, variant_data in enumerate(
                variants
            ):

                variant_id = variant_data.get("id")

                if variant_id:

                    try:
                        variant = (
                            FoodItemVariant.objects
                            .get(
                                id=variant_id,
                                food_item=food_item,
                            )
                        )

                    except FoodItemVariant.DoesNotExist:
                        raise ValidationError(
                            {
                                "variants": (
                                    f"Variant "
                                    f"{variant_id} "
                                    "does not belong "
                                    "to this food item."
                                )
                            }
                        )

                    submitted_variant_ids.add(
                        variant.id
                    )

                    variant.name = (
                        variant_data["name"]
                        .strip()
                    )

                    variant.price = (
                        variant_data["price"]
                    )

                    variant.is_default = (
                        variant_data.get(
                            "is_default",
                            False,
                        )
                    )

                    variant.is_available = (
                        variant_data.get(
                            "is_available",
                            True,
                        )
                    )

                    variant.display_order = (
                        variant_data.get(
                            "display_order",
                            index,
                        )
                    )

                    variant.save()

                else:

                    variant = (
                        FoodItemVariant.objects
                        .create(
                            food_item=food_item,
                            name=(
                                variant_data["name"]
                                .strip()
                            ),
                            price=variant_data[
                                "price"
                            ],
                            is_default=variant_data.get(
                                "is_default",
                                False,
                            ),
                            is_available=variant_data.get(
                                "is_available",
                                True,
                            ),
                            display_order=variant_data.get(
                                "display_order",
                                index,
                            ),
                        )
                    )

                    submitted_variant_ids.add(
                        variant.id
                    )

            # Delete removed variants
            FoodItemVariant.objects.filter(
                food_item=food_item
            ).exclude(
                id__in=submitted_variant_ids
            ).delete()

            # Guarantee a default
            if not FoodItemVariant.objects.filter(
                food_item=food_item,
                is_default=True,
            ).exists():

                first_variant = (
                    FoodItemVariant.objects
                    .filter(
                        food_item=food_item
                    )
                    .order_by(
                        "display_order",
                        "created_at",
                    )
                    .first()
                )

                if first_variant:
                    first_variant.is_default = True
                    first_variant.save(
                        update_fields=[
                            "is_default",
                            "updated_at",
                        ]
                    )

        # ------------------------------------------------------
        # ADDONS
        # ------------------------------------------------------

        if "addons" in data:

            addons = data["addons"]

            submitted_addon_ids = set()

            for index, addon_data in enumerate(
                addons
            ):

                addon_id = addon_data.get("id")

                if addon_id:

                    try:
                        addon = (
                            FoodItemAddon.objects
                            .get(
                                id=addon_id,
                                food_item=food_item,
                            )
                        )

                    except FoodItemAddon.DoesNotExist:
                        raise ValidationError(
                            {
                                "addons": (
                                    f"Addon "
                                    f"{addon_id} "
                                    "does not belong "
                                    "to this food item."
                                )
                            }
                        )

                    submitted_addon_ids.add(
                        addon.id
                    )

                    addon.name = (
                        addon_data["name"]
                        .strip()
                    )

                    addon.price = (
                        addon_data["price"]
                    )

                    addon.is_required = (
                        addon_data.get(
                            "is_required",
                            False,
                        )
                    )

                    addon.max_quantity = (
                        addon_data.get(
                            "max_quantity",
                            1,
                        )
                    )

                    addon.is_available = (
                        addon_data.get(
                            "is_available",
                            True,
                        )
                    )

                    addon.display_order = (
                        addon_data.get(
                            "display_order",
                            index,
                        )
                    )

                    addon.save()

                else:

                    addon = (
                        FoodItemAddon.objects
                        .create(
                            food_item=food_item,
                            name=(
                                addon_data["name"]
                                .strip()
                            ),
                            price=addon_data[
                                "price"
                            ],
                            is_required=addon_data.get(
                                "is_required",
                                False,
                            ),
                            max_quantity=addon_data.get(
                                "max_quantity",
                                1,
                            ),
                            is_available=addon_data.get(
                                "is_available",
                                True,
                            ),
                            display_order=addon_data.get(
                                "display_order",
                                index,
                            ),
                        )
                    )

                    submitted_addon_ids.add(
                        addon.id
                    )

            FoodItemAddon.objects.filter(
                food_item=food_item
            ).exclude(
                id__in=submitted_addon_ids
            ).delete()

        return food_item



    @staticmethod
    def get_food_items():

        return (
            FoodItem.objects
            .select_related("category")
            .prefetch_related(
                "variants",
                "addons",
            )
            .order_by(
                "display_order",
                "created_at",
            )
        )

    @staticmethod
    def get_food_item(food_item_id):

        try:
            return (
                FoodItem.objects
                .select_related("category")
                .prefetch_related(
                    "variants",
                    "addons",
                )
                .get(id=food_item_id)
            )

        except FoodItem.DoesNotExist:
            raise ValidationError(
                "Food item not found."
            )

    @staticmethod
    @transaction.atomic
    def delete_food_item(food_item_id):

        try:
            food_item = (
                FoodItem.objects
                .select_for_update()
                .get(id=food_item_id)
            )

        except FoodItem.DoesNotExist:
            raise ValidationError(
                "Food item not found."
            )

        # Do not physically delete if it has
        # already been ordered.
        if food_item.order_items.exists():
            food_item.is_active = False
            food_item.is_available = False

            food_item.save(
                update_fields=[
                    "is_active",
                    "is_available",
                    "updated_at",
                ]
            )

            return food_item

        food_item.delete()

        return None