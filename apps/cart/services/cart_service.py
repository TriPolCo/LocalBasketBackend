from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.cart.models.cart import Cart
from apps.cart.models.cart_item import CartItem
from apps.products.models.variant import ProductVariant


class CartService:

    # =====================================================
    # GET / CREATE CART
    # =====================================================

    @staticmethod
    def get_or_create_cart(customer):

        cart, _ = Cart.objects.get_or_create(
            customer=customer
        )

        return cart

    # =====================================================
    # GET CART
    # =====================================================

    @staticmethod
    def get_cart(customer):

        cart = (
            Cart.objects
            .filter(customer=customer)
            .prefetch_related(
                "items__variant__product",
                "items__variant__images",
                "items__variant__variant_values__value",
            )
            .first()
        )

        if not cart:
            cart = Cart.objects.create(
                customer=customer
            )

        return cart

    # =====================================================
    # ADD TO CART
    # =====================================================

    @staticmethod
    @transaction.atomic
    def add_to_cart(
        customer,
        variant_id,
        quantity,
    ):

        variant = (
            ProductVariant.objects
            .select_for_update()
            .select_related("product")
            .filter(
                id=variant_id,
                is_active=True,
                product__is_active=True,
            )
            .first()
        )

        if not variant:
            raise ValidationError(
                "Product variant not found or inactive."
            )

        if variant.stock <= 0:
            raise ValidationError(
                "Product is out of stock."
            )

        if quantity > variant.stock:
            raise ValidationError(
                {
                    "quantity": (
                        f"Only {variant.stock} "
                        "units are available."
                    )
                }
            )

        cart, _ = Cart.objects.get_or_create(
            customer=customer
        )

        cart_item = (
            CartItem.objects
            .select_for_update()
            .filter(
                cart=cart,
                variant=variant,
            )
            .first()
        )

        if cart_item:

            new_quantity = (
                cart_item.quantity + quantity
            )

            if new_quantity > variant.stock:
                raise ValidationError(
                    {
                        "quantity": (
                            f"Only {variant.stock} "
                            "units are available."
                        )
                    }
                )

            cart_item.quantity = new_quantity

            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

        else:

            cart_item = CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=quantity,
            )

        cart.save(
            update_fields=["updated_at"]
        )

        return cart_item

    # =====================================================
    # UPDATE QUANTITY
    # =====================================================

    @staticmethod
    @transaction.atomic
    def update_quantity(
        customer,
        item_id,
        quantity,
    ):

        cart = Cart.objects.filter(
            customer=customer
        ).first()

        if not cart:
            raise ValidationError(
                "Cart not found."
            )

        cart_item = (
            CartItem.objects
            .select_for_update()
            .select_related("variant")
            .filter(
                id=item_id,
                cart=cart,
            )
            .first()
        )

        if not cart_item:
            raise ValidationError(
                "Cart item not found."
            )

        variant = cart_item.variant

        if not variant.is_active:
            raise ValidationError(
                "Product variant is inactive."
            )

        if variant.stock <= 0:
            raise ValidationError(
                "Product is out of stock."
            )

        if quantity > variant.stock:
            raise ValidationError(
                {
                    "quantity": (
                        f"Only {variant.stock} "
                        "units are available."
                    )
                }
            )

        cart_item.quantity = quantity

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        cart.save(
            update_fields=["updated_at"]
        )

        return cart_item

    # =====================================================
    # INCREASE QUANTITY
    # =====================================================

    @staticmethod
    @transaction.atomic
    def increase_quantity(
        customer,
        item_id,
    ):

        cart = Cart.objects.filter(
            customer=customer
        ).first()

        if not cart:
            raise ValidationError(
                "Cart not found."
            )

        cart_item = (
            CartItem.objects
            .select_for_update()
            .select_related("variant")
            .filter(
                id=item_id,
                cart=cart,
            )
            .first()
        )

        if not cart_item:
            raise ValidationError(
                "Cart item not found."
            )

        variant = cart_item.variant

        if not variant.is_active:
            raise ValidationError(
                "Product variant is inactive."
            )

        new_quantity = cart_item.quantity + 1

        if new_quantity > variant.stock:
            raise ValidationError(
                {
                    "quantity": (
                        f"Only {variant.stock} "
                        "units are available."
                    )
                }
            )

        cart_item.quantity = new_quantity

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        cart.save(
            update_fields=["updated_at"]
        )

        return cart_item

    # =====================================================
    # DECREASE QUANTITY
    # =====================================================

    @staticmethod
    @transaction.atomic
    def decrease_quantity(
        customer,
        item_id,
    ):

        cart = Cart.objects.filter(
            customer=customer
        ).first()

        if not cart:
            raise ValidationError(
                "Cart not found."
            )

        cart_item = (
            CartItem.objects
            .select_for_update()
            .filter(
                id=item_id,
                cart=cart,
            )
            .first()
        )

        if not cart_item:
            raise ValidationError(
                "Cart item not found."
            )

        if cart_item.quantity == 1:

            cart_item.delete()

            cart.save(
                update_fields=["updated_at"]
            )

            return None

        cart_item.quantity -= 1

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        cart.save(
            update_fields=["updated_at"]
        )

        return cart_item

    # =====================================================
    # REMOVE ITEM
    # =====================================================

    @staticmethod
    @transaction.atomic
    def remove_item(
        customer,
        item_id,
    ):

        cart = Cart.objects.filter(
            customer=customer
        ).first()

        if not cart:
            raise ValidationError(
                "Cart not found."
            )

        cart_item = CartItem.objects.filter(
            id=item_id,
            cart=cart,
        ).first()

        if not cart_item:
            raise ValidationError(
                "Cart item not found."
            )

        cart_item.delete()

        cart.save(
            update_fields=["updated_at"]
        )

    # =====================================================
    # CLEAR CART
    # =====================================================

    @staticmethod
    @transaction.atomic
    def clear_cart(customer):

        cart = Cart.objects.filter(
            customer=customer
        ).first()

        if not cart:
            return

        cart.items.all().delete()

        cart.save(
            update_fields=["updated_at"]
        )