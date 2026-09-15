import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.address.models.address import Address

from apps.food.models.food_cart import FoodCart
from apps.food.models.food_cart_item import FoodCartItem
from apps.food.models.food_order import FoodOrder
from apps.food.models.food_order_item import FoodOrderItem
from apps.food.models.food_order_item_addon import FoodOrderItemAddon


class FoodOrderService:

    DELIVERY_FEE = Decimal("0.00")
    PACKAGING_FEE = Decimal("0.00")
    TAX = Decimal("0.00")
    DISCOUNT = Decimal("0.00")

    @staticmethod
    def _generate_order_number():
        while True:
            number = (
                f"FO-{timezone.now():%Y%m%d}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

            if not FoodOrder.objects.filter(
                order_number=number
            ).exists():
                return number

    @staticmethod
    @transaction.atomic
    def place_order(
        customer,
        address_id,
        payment_method,
        customer_note=None,
    ):
        if payment_method != FoodOrder.PaymentMethod.COD:
            raise ValidationError({
                "payment_method": (
                    "Online payment is not available yet."
                )
            })

        try:
            address = (
                Address.objects
                .select_for_update()
                .get(
                    id=address_id,
                    customer=customer,
                )
            )
        except Address.DoesNotExist:
            raise ValidationError({
                "address_id": "Address not found."
            })

        try:
            cart = (
                FoodCart.objects
                .select_for_update()
                .get(customer=customer)
            )
        except FoodCart.DoesNotExist:
            raise ValidationError({
                "cart": "Food cart is empty."
            })

        cart_items = list(
            FoodCartItem.objects
            .select_for_update()
            .filter(cart=cart)
            .select_related(
                "food_item",
                "variant",
            )
            .prefetch_related(
                "addons__addon",
            )
        )

        if not cart_items:
            raise ValidationError({
                "cart": "Food cart is empty."
            })

        subtotal = Decimal("0.00")

        order_items_data = []

        for cart_item in cart_items:

            food_item = cart_item.food_item
            variant = cart_item.variant

            if not food_item.is_active:
                raise ValidationError({
                    "food_item": (
                        f"{food_item.name} is no longer available."
                    )
                })

            if not food_item.is_available:
                raise ValidationError({
                    "food_item": (
                        f"{food_item.name} is currently unavailable."
                    )
                })

            if not variant.is_available:
                raise ValidationError({
                    "variant": (
                        f"{variant.name} is currently unavailable."
                    )
                })

            item_quantity = cart_item.quantity

            base_total = (
                variant.price * item_quantity
            )

            addon_total = Decimal("0.00")
            addon_snapshots = []

            for cart_addon in cart_item.addons.all():

                addon = cart_addon.addon

                if not addon.is_available:
                    raise ValidationError({
                        "addon": (
                            f"{addon.name} is no longer available."
                        )
                    })

                if cart_addon.quantity > addon.max_quantity:
                    raise ValidationError({
                        "addon": (
                            f"{addon.name} allows maximum "
                            f"{addon.max_quantity}."
                        )
                    })

                total_amount = (
                    addon.price
                    * cart_addon.quantity
                    * item_quantity
                )

                addon_total += total_amount

                addon_snapshots.append({
                    "addon": addon,
                    "addon_name": addon.name,
                    "unit_price": addon.price,
                    "quantity": cart_addon.quantity,
                    "total_amount": total_amount,
                })

            item_total = base_total + addon_total

            subtotal += item_total

            order_items_data.append({
                "cart_item": cart_item,
                "food_item": food_item,
                "variant": variant,
                "quantity": item_quantity,
                "addon_total": addon_total,
                "item_total": item_total,
                "addons": addon_snapshots,
            })

        delivery_fee = FoodOrderService.DELIVERY_FEE
        packaging_fee = FoodOrderService.PACKAGING_FEE
        discount = FoodOrderService.DISCOUNT
        tax = FoodOrderService.TAX

        total_amount = (
            subtotal
            + delivery_fee
            + packaging_fee
            + tax
            - discount
        )

        order = FoodOrder.objects.create(
            order_number=FoodOrderService._generate_order_number(),

            customer=customer,

            status=FoodOrder.Status.PENDING,

            payment_method=payment_method,
            payment_status=FoodOrder.PaymentStatus.PENDING,

            subtotal=subtotal,
            delivery_fee=delivery_fee,
            packaging_fee=packaging_fee,
            discount=discount,
            tax=tax,
            total_amount=total_amount,

            shipping_full_name=address.full_name,
            shipping_phone_number=address.phone_number,
            shipping_address_line_1=address.address_line_1,
            shipping_address_line_2=address.address_line_2,
            shipping_landmark=address.landmark,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,

            customer_note=customer_note,
        )

        for data in order_items_data:

            food_item = data["food_item"]
            variant = data["variant"]

            order_item = FoodOrderItem.objects.create(
                order=order,

                food_item=food_item,
                variant=variant,

                food_name=food_item.name,
                food_type=food_item.food_type,
                food_image_url=food_item.image_url,

                variant_name=variant.name,

                unit_price=variant.price,
                quantity=data["quantity"],

                addon_total=data["addon_total"],
                item_total=data["item_total"],
            )

            for addon_data in data["addons"]:
                FoodOrderItemAddon.objects.create(
                    order_item=order_item,

                    addon=addon_data["addon"],

                    addon_name=addon_data["addon_name"],
                    unit_price=addon_data["unit_price"],
                    quantity=addon_data["quantity"],
                    total_amount=addon_data["total_amount"],
                )

        FoodCartItem.objects.filter(
            cart=cart
        ).delete()

        return FoodOrderService.get_order(
            customer=customer,
            order_id=order.id,
        )

    @staticmethod
    def get_orders(customer):
        return (
            FoodOrder.objects
            .filter(customer=customer)
            .prefetch_related(
                "items__addons",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_order(customer, order_id):
        try:
            return (
                FoodOrder.objects
                .filter(
                    id=order_id,
                    customer=customer,
                )
                .prefetch_related(
                    "items__addons",
                )
                .get()
            )
        except FoodOrder.DoesNotExist:
            raise ValidationError({
                "order": "Food order not found."
            })

    @staticmethod
    @transaction.atomic
    def cancel_order(customer, order_id):

        try:
            order = (
                FoodOrder.objects
                .select_for_update()
                .get(
                    id=order_id,
                    customer=customer,
                )
            )
        except FoodOrder.DoesNotExist:
            raise ValidationError({
                "order": "Food order not found."
            })

        cancellable_statuses = [
            FoodOrder.Status.PENDING,
            FoodOrder.Status.CONFIRMED,
        ]

        if order.status not in cancellable_statuses:
            raise ValidationError({
                "status": (
                    "This order cannot be cancelled now."
                )
            })

        order.status = FoodOrder.Status.CANCELLED
        order.cancelled_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_at",
            ]
        )

        return order