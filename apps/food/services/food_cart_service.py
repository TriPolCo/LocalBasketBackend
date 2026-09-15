from django.db import transaction
from django.core.exceptions import ValidationError

from apps.food.models.food_cart import FoodCart
from apps.food.models.food_cart_item import FoodCartItem
from apps.food.models.food_cart_item_addon import FoodCartItemAddon
from apps.food.models.food_item import FoodItem
from apps.food.models.food_item_variant import FoodItemVariant
from apps.food.models.food_item_addon import FoodItemAddon


class FoodCartService:

    @staticmethod
    def get_or_create_cart(customer):
        cart, _ = FoodCart.objects.get_or_create(
            customer=customer
        )
        return cart

    @staticmethod
    def get_cart(customer):
        cart = FoodCartService.get_or_create_cart(customer)

        return (
            FoodCart.objects
            .filter(id=cart.id)
            .prefetch_related(
                "items__food_item",
                "items__variant",
                "items__addons__addon",
            )
            .get()
        )

    @staticmethod
    @transaction.atomic
    def add_item(
        customer,
        food_item_id,
        variant_id,
        quantity,
        addons=None,
    ):
        addons = addons or []

        cart = (
            FoodCart.objects
            .select_for_update()
            .get_or_create(customer=customer)[0]
        )

        try:
            food_item = (
                FoodItem.objects
                .select_for_update()
                .get(
                    id=food_item_id,
                    is_active=True,
                    is_available=True,
                )
            )
        except FoodItem.DoesNotExist:
            raise ValidationError({
                "food_item": "Food item is not available."
            })

        try:
            variant = (
                FoodItemVariant.objects
                .get(
                    id=variant_id,
                    food_item=food_item,
                    is_available=True,
                )
            )
        except FoodItemVariant.DoesNotExist:
            raise ValidationError({
                "variant": "Selected variant is not available."
            })

        validated_addons = FoodCartService._validate_addons(
            food_item=food_item,
            addons=addons,
        )

        item, created = (
            FoodCartItem.objects
            .select_for_update()
            .get_or_create(
                cart=cart,
                variant=variant,
                defaults={
                    "food_item": food_item,
                    "quantity": quantity,
                },
            )
        )

        if not created:
            item.quantity += quantity
            item.food_item = food_item
            item.save(
                update_fields=[
                    "quantity",
                    "food_item",
                    "updated_at",
                ]
            )

        for addon, addon_quantity in validated_addons:
            cart_addon, created = (
                FoodCartItemAddon.objects
                .get_or_create(
                    cart_item=item,
                    addon=addon,
                    defaults={
                        "quantity": addon_quantity,
                    },
                )
            )

            if not created:
                cart_addon.quantity += addon_quantity
                cart_addon.save(
                    update_fields=[
                        "quantity",
                        "updated_at",
                    ]
                )

        return FoodCartService.get_cart(customer)

    @staticmethod
    @transaction.atomic
    def update_item(
        customer,
        item_id,
        quantity=None,
        addons=None,
    ):
        cart = FoodCartService.get_or_create_cart(customer)

        try:
            item = (
                FoodCartItem.objects
                .select_for_update()
                .get(
                    id=item_id,
                    cart=cart,
                )
            )
        except FoodCartItem.DoesNotExist:
            raise ValidationError({
                "item": "Cart item not found."
            })

        if quantity is not None:
            item.quantity = quantity
            item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

        if addons is not None:
            validated_addons = FoodCartService._validate_addons(
                food_item=item.food_item,
                addons=addons,
            )

            item.addons.all().delete()

            for addon, addon_quantity in validated_addons:
                FoodCartItemAddon.objects.create(
                    cart_item=item,
                    addon=addon,
                    quantity=addon_quantity,
                )

        return FoodCartService.get_cart(customer)

    @staticmethod
    @transaction.atomic
    def increase_item(customer, item_id):
        cart = FoodCartService.get_or_create_cart(customer)

        try:
            item = (
                FoodCartItem.objects
                .select_for_update()
                .get(
                    id=item_id,
                    cart=cart,
                )
            )
        except FoodCartItem.DoesNotExist:
            raise ValidationError({
                "item": "Cart item not found."
            })

        item.quantity += 1
        item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        return FoodCartService.get_cart(customer)

    @staticmethod
    @transaction.atomic
    def decrease_item(customer, item_id):
        cart = FoodCartService.get_or_create_cart(customer)

        try:
            item = (
                FoodCartItem.objects
                .select_for_update()
                .get(
                    id=item_id,
                    cart=cart,
                )
            )
        except FoodCartItem.DoesNotExist:
            raise ValidationError({
                "item": "Cart item not found."
            })

        if item.quantity <= 1:
            item.delete()
        else:
            item.quantity -= 1
            item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

        return FoodCartService.get_cart(customer)

    @staticmethod
    @transaction.atomic
    def remove_item(customer, item_id):
        cart = FoodCartService.get_or_create_cart(customer)

        deleted, _ = FoodCartItem.objects.filter(
            id=item_id,
            cart=cart,
        ).delete()

        if deleted == 0:
            raise ValidationError({
                "item": "Cart item not found."
            })

        return FoodCartService.get_cart(customer)

    @staticmethod
    @transaction.atomic
    def clear_cart(customer):
        cart = FoodCartService.get_or_create_cart(customer)

        FoodCartItem.objects.filter(
            cart=cart
        ).delete()

        return FoodCartService.get_cart(customer)

    @staticmethod
    def _validate_addons(food_item, addons):
        if not isinstance(addons, list):
            raise ValidationError({
                "addons": "Addons must be a list."
            })

        requested = {}

        for addon_data in addons:
            addon_id = addon_data["addon_id"]
            quantity = addon_data.get("quantity", 1)

            if addon_id in requested:
                requested[addon_id] += quantity
            else:
                requested[addon_id] = quantity

        available_addons = {
            str(addon.id): addon
            for addon in FoodItemAddon.objects.filter(
                food_item=food_item,
                is_available=True,
            )
        }

        result = []

        for addon_id, quantity in requested.items():

            addon = available_addons.get(str(addon_id))

            if not addon:
                raise ValidationError({
                    "addon": (
                        f"Addon {addon_id} is not available "
                        "for this food item."
                    )
                })

            if quantity > addon.max_quantity:
                raise ValidationError({
                    "addon": (
                        f"{addon.name} allows maximum "
                        f"{addon.max_quantity}."
                    )
                })

            result.append(
                (addon, quantity)
            )

        required_addons = [
            addon
            for addon in available_addons.values()
            if addon.is_required
        ]

        selected_ids = {
            str(addon.id)
            for addon, _ in result
        }

        missing_required = [
            addon.name
            for addon in required_addons
            if str(addon.id) not in selected_ids
        ]

        if missing_required:
            raise ValidationError({
                "addons": (
                    "Required addons missing: "
                    + ", ".join(missing_required)
                )
            })

        return result