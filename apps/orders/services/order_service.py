from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.exceptions import ValidationError

from apps.address.models.address import Address
from apps.cart.models.cart import Cart
from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderItem
from apps.products.models.variant import ProductVariant


class OrderService:

    # --------------------------------------------------
    # ORDER NUMBER
    # --------------------------------------------------

    @staticmethod
    def generate_order_number():

        while True:

            order_number = (
                f"LB-"
                f"{timezone.now().strftime('%Y%m%d')}-"
                f"{get_random_string(5, '0123456789')}"
            )

            if not Order.objects.filter(
                order_number=order_number
            ).exists():

                return order_number

    # --------------------------------------------------
    # PLACE ORDER
    # --------------------------------------------------

    @staticmethod
    @transaction.atomic
    def place_order(
        customer,
        cart_id,
        address_id,
    ):

        # ----------------------------------------------
        # GET CART
        # ----------------------------------------------

        cart = (
            Cart.objects
            .select_for_update()
            .filter(
                id=cart_id,
                customer=customer,
            )
            .first()
        )

        if not cart:
            raise ValidationError(
                "Cart not found."
            )

        # ----------------------------------------------
        # GET CART ITEMS
        # ----------------------------------------------

        cart_items = list(
            cart.items
            .select_related(
                "variant",
                "variant__product",
            )
            .all()
        )

        if not cart_items:
            raise ValidationError(
                "Your cart is empty."
            )

        # ----------------------------------------------
        # GET ADDRESS
        # ----------------------------------------------

        address = (
            Address.objects
            .select_for_update()
            .filter(
                id=address_id,
                customer=customer,
            )
            .first()
        )

        if not address:
            raise ValidationError(
                "Address not found."
            )

        # ----------------------------------------------
        # LOCK ALL VARIANTS
        # ----------------------------------------------

        variant_ids = [
            item.variant_id
            for item in cart_items
        ]

        locked_variants = {
            variant.id: variant
            for variant in (
                ProductVariant.objects
                .select_for_update()
                .select_related("product")
                .filter(
                    id__in=variant_ids
                )
            )
        }

        # ----------------------------------------------
        # VALIDATE ITEMS
        # ----------------------------------------------

        subtotal = Decimal("0.00")

        validated_items = []

        for cart_item in cart_items:

            variant = locked_variants.get(
                cart_item.variant_id
            )

            if not variant:
                raise ValidationError(
                    f"Product variant for "
                    f"{cart_item.variant.sku} "
                    f"is no longer available."
                )

            if not variant.is_active:
                raise ValidationError(
                    f"{variant.product.name} "
                    f"is currently unavailable."
                )

            if not variant.product.is_active:
                raise ValidationError(
                    f"{variant.product.name} "
                    f"is currently unavailable."
                )

            # ------------------------------------------
            # STOCK CHECK
            # ------------------------------------------

            if variant.stock <= 0:
                raise ValidationError(
                    f"{variant.product.name} "
                    f"is out of stock."
                )

            if cart_item.quantity > variant.stock:

                raise ValidationError({
                    "quantity": (
                        f"Only {variant.stock} units "
                        f"of {variant.product.name} "
                        f"are available."
                    )
                })

            # ------------------------------------------
            # CURRENT PRICE
            # ------------------------------------------

            current_price = variant.selling_price
            current_mrp = variant.mrp

            item_total = (
                current_price *
                cart_item.quantity
            )

            subtotal += item_total

            validated_items.append(
                {
                    "cart_item": cart_item,
                    "variant": variant,
                    "product": variant.product,
                    "mrp": current_mrp,
                    "selling_price": current_price,
                    "item_total": item_total,
                }
            )

        # ----------------------------------------------
        # ORDER AMOUNTS
        # ----------------------------------------------

        delivery_fee = Decimal("0.00")
        discount = Decimal("0.00")
        tax = Decimal("0.00")

        total_amount = (
            subtotal
            + delivery_fee
            + tax
            - discount
        )

        # ----------------------------------------------
        # CREATE ORDER
        # ----------------------------------------------

        order = Order.objects.create(
            order_number=OrderService.generate_order_number(),

            customer=customer,

            shipping_address=address,

            # Address snapshot
            shipping_full_name=address.full_name,
            shipping_phone_number=address.phone_number,

            shipping_address_line_1=(
                address.address_line_1
            ),

            shipping_address_line_2=(
                address.address_line_2
            ),

            shipping_landmark=(
                address.landmark
            ),

            shipping_city=address.city,
            shipping_state=address.state,

            shipping_postal_code=(
                address.postal_code
            ),

            shipping_country=address.country,

            # COD
            payment_method="COD",
            payment_status=(
                Order.PaymentStatus.PENDING
            ),

            # Amounts
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            tax=tax,
            total_amount=total_amount,

            # Status
            status=Order.Status.PROCESSING,
        )

        # ----------------------------------------------
        # CREATE ORDER ITEMS
        # ----------------------------------------------

        for item_data in validated_items:

            cart_item = item_data["cart_item"]
            variant = item_data["variant"]
            product = item_data["product"]

            OrderItem.objects.create(

                order=order,

                product=product,
                variant=variant,

                # Product snapshot
                product_name=product.name,
                sku=variant.sku,

                # Quantity
                quantity=cart_item.quantity,

                # Price snapshot
                mrp=item_data["mrp"],
                selling_price=item_data[
                    "selling_price"
                ],

                item_discount=Decimal("0.00"),

                item_total=item_data[
                    "item_total"
                ],
            )

        # ----------------------------------------------
        # REDUCE STOCK
        # ----------------------------------------------

        for item_data in validated_items:

            variant = item_data["variant"]
            quantity = item_data[
                "cart_item"
            ].quantity

            variant.stock -= quantity

            variant.save(
                update_fields=[
                    "stock",
                    "updated_at",
                ]
            )

        # ----------------------------------------------
        # CLEAR CART
        # ----------------------------------------------

        cart.items.all().delete()

        cart.save(
            update_fields=[
                "updated_at"
            ]
        )

        return order

    # --------------------------------------------------
    # GET CUSTOMER ORDERS
    # --------------------------------------------------

    @staticmethod
    def get_orders(customer):

        return (
            Order.objects
            .filter(
                customer=customer
            )
            .prefetch_related(
                "items"
            )
            .select_related(
                "shipping_address"
            )
            .order_by(
                "-created_at"
            )
        )

    # --------------------------------------------------
    # GET SINGLE ORDER
    # --------------------------------------------------

    @staticmethod
    def get_order(
        customer,
        order_id,
    ):

        order = (
            Order.objects
            .filter(
                id=order_id,
                customer=customer,
            )
            .select_related(
                "shipping_address"
            )
            .prefetch_related(
                "items"
            )
            .first()
        )

        if not order:
            raise ValidationError(
                "Order not found."
            )

        return order

    # --------------------------------------------------
    # CANCEL ORDER
    # --------------------------------------------------

    @staticmethod
    @transaction.atomic
    def cancel_order(
        customer,
        order_id,
    ):

        order = (
            Order.objects
            .select_for_update()
            .filter(
                id=order_id,
                customer=customer,
            )
            .first()
        )

        if not order:
            raise ValidationError(
                "Order not found."
            )

        # Only processing orders can be cancelled
        if order.status != Order.Status.PROCESSING:

            raise ValidationError(
                "This order can no longer be cancelled."
            )

        order_items = list(
            order.items
            .select_related(
                "variant"
            )
            .all()
        )

        # ----------------------------------------------
        # RESTORE STOCK
        # ----------------------------------------------

        for order_item in order_items:

            variant = (
                ProductVariant.objects
                .select_for_update()
                .filter(
                    id=order_item.variant_id
                )
                .first()
            )

            if variant:
                variant.stock += order_item.quantity

                variant.save(
                    update_fields=[
                        "stock",
                        "updated_at",
                    ]
                )

        # ----------------------------------------------
        # CANCEL ORDER
        # ----------------------------------------------

        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_at",
            ]
        )

        return order