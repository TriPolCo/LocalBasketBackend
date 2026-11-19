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
from apps.notifications.pusher_service import trigger_admin_order_notification


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
    # PLACE REGULAR CART ORDER
    # --------------------------------------------------

    @staticmethod
    @transaction.atomic
    def place_order(
        customer,
        cart_id,
        address_id,
    ):

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

        subtotal = Decimal("0.00")
        validated_items = []

        for cart_item in cart_items:

            variant = locked_variants.get(
                cart_item.variant_id
            )

            if not variant:
                raise ValidationError(
                    f"Product variant for {cart_item.variant.sku} is no longer available."
                )

            if not variant.is_active or not variant.product.is_active:
                raise ValidationError(
                    f"{variant.product.name} is currently unavailable."
                )

            if variant.stock <= 0:
                raise ValidationError(
                    f"{variant.product.name} is out of stock."
                )

            if cart_item.quantity > variant.stock:
                raise ValidationError({
                    "quantity": f"Only {variant.stock} units of {variant.product.name} are available."
                })

            current_price = variant.selling_price
            current_mrp = variant.mrp
            item_total = current_price * cart_item.quantity
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

        delivery_fee = Decimal("0.00")
        discount = Decimal("0.00")
        tax = Decimal("0.00")
        total_amount = subtotal + delivery_fee + tax - discount

        order = Order.objects.create(
            order_number=OrderService.generate_order_number(),
            customer=customer,
            order_type=Order.OrderType.REGULAR,
            manual_items=[],
            shipping_address=address,
            shipping_full_name=address.full_name,
            shipping_phone_number=address.phone_number,
            shipping_address_line_1=address.address_line_1,
            shipping_address_line_2=address.address_line_2,
            shipping_landmark=address.landmark,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,
            payment_method="COD",
            payment_status=Order.PaymentStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            tax=tax,
            total_amount=total_amount,
            status=Order.Status.PROCESSING,
        )

        for item_data in validated_items:
            cart_item = item_data["cart_item"]
            variant = item_data["variant"]
            product = item_data["product"]

            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                product_name=product.name,
                sku=variant.sku,
                quantity=cart_item.quantity,
                mrp=item_data["mrp"],
                selling_price=item_data["selling_price"],
                item_discount=Decimal("0.00"),
                item_total=item_data["item_total"],
            )

        for item_data in validated_items:
            variant = item_data["variant"]
            quantity = item_data["cart_item"].quantity
            variant.stock -= quantity
            variant.save(update_fields=["stock", "updated_at"])

        cart.items.all().delete()
        cart.save(update_fields=["updated_at"])

        return order

    # --------------------------------------------------
    # PLACE UPLOAD PAPER LIST ORDER (STRING URL)
    # --------------------------------------------------

    @staticmethod
    @transaction.atomic
    def place_upload_list_order(
        customer,
        address_id,
        image_url,
        instructions="",
    ):

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

        if not image_url or not str(image_url).strip():
            raise ValidationError(
                "image_url string is required."
            )

        order = Order.objects.create(
            order_number=OrderService.generate_order_number(),
            customer=customer,
            order_type=Order.OrderType.IMAGE_LIST,
            list_image_url=str(image_url).strip(),
            special_instructions=instructions,
            manual_items=[],
            shipping_address=address,
            shipping_full_name=address.full_name,
            shipping_phone_number=address.phone_number,
            shipping_address_line_1=address.address_line_1,
            shipping_address_line_2=address.address_line_2,
            shipping_landmark=address.landmark,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,
            payment_method="COD",
            payment_status=Order.PaymentStatus.PENDING,
            subtotal=Decimal("0.00"),
            delivery_fee=Decimal("0.00"),
            discount=Decimal("0.00"),
            tax=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            status=Order.Status.PROCESSING,
        )

        # Trigger Real-time WebSocket Notification
        trigger_admin_order_notification({
            "id": str(order.id),
            "order_number": order.order_number,
            "order_type": "IMAGE_LIST",
            "list_image_url": str(image_url).strip(),
            "status": order.status,
            "total_price": "Pending Calculation",
            "customer": {
                "name": order.shipping_full_name,
                "phone": order.shipping_phone_number,
                "city": order.shipping_city,
            },
            "instructions": instructions,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

        return order

    # --------------------------------------------------
    # PLACE TYPED WRITTEN LIST ORDER
    # --------------------------------------------------

    @staticmethod
    @transaction.atomic
    def place_type_list_order(
        customer,
        address_id,
        items_raw,
        instructions="",
    ):

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

        if not items_raw or not str(items_raw).strip():
            raise ValidationError(
                "Items list cannot be empty."
            )

        order = Order.objects.create(
            order_number=OrderService.generate_order_number(),
            customer=customer,
            order_type=Order.OrderType.TEXT_LIST,
            list_text_content=str(items_raw).strip(),
            special_instructions=instructions,
            manual_items=[],
            shipping_address=address,
            shipping_full_name=address.full_name,
            shipping_phone_number=address.phone_number,
            shipping_address_line_1=address.address_line_1,
            shipping_address_line_2=address.address_line_2,
            shipping_landmark=address.landmark,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,
            payment_method="COD",
            payment_status=Order.PaymentStatus.PENDING,
            subtotal=Decimal("0.00"),
            delivery_fee=Decimal("0.00"),
            discount=Decimal("0.00"),
            tax=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            status=Order.Status.PROCESSING,
        )

        # Trigger Real-time WebSocket Notification
        trigger_admin_order_notification({
            "id": str(order.id),
            "order_number": order.order_number,
            "order_type": "TEXT_LIST",
            "list_text_content": str(items_raw).strip(),
            "status": order.status,
            "total_price": "Pending Calculation",
            "customer": {
                "name": order.shipping_full_name,
                "phone": order.shipping_phone_number,
                "city": order.shipping_city,
            },
            "instructions": instructions,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

        return order

    # --------------------------------------------------
    # GET CUSTOMER ORDERS
    # --------------------------------------------------

    @staticmethod
    def get_orders(customer):
        return (
            Order.objects
            .filter(customer=customer)
            .select_related("shipping_address")
            .prefetch_related("items", "items__variant__images")
            .order_by("-created_at")
        )

    # --------------------------------------------------
    # GET SINGLE ORDER
    # --------------------------------------------------

    @staticmethod
    def get_order(customer, order_id):
        order = (
            Order.objects
            .filter(id=order_id, customer=customer)
            .select_related("shipping_address")
            .prefetch_related("items", "items__variant__images")
            .first()
        )
        if not order:
            raise ValidationError("Order not found.")
        return order

    # --------------------------------------------------
    # CANCEL ORDER
    # --------------------------------------------------

    @staticmethod
    @transaction.atomic
    def cancel_order(customer, order_id):
        order = (
            Order.objects
            .select_for_update()
            .filter(id=order_id, customer=customer)
            .first()
        )
        if not order:
            raise ValidationError("Order not found.")

        if order.status not in [
            Order.Status.PROCESSING,
            Order.Status.PENDING_REVIEW,
        ]:
            raise ValidationError("This order can no longer be cancelled.")

        order_items = list(order.items.select_related("variant").all())

        for order_item in order_items:
            variant = (
                ProductVariant.objects
                .select_for_update()
                .filter(id=order_item.variant_id)
                .first()
            )
            if variant:
                variant.stock += order_item.quantity
                variant.save(update_fields=["stock", "updated_at"])

        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at", "updated_at"])

        return order

    @staticmethod
    @transaction.atomic
    def update_order_status(order, new_status):
        old_status = order.status

        if old_status == new_status:
            raise ValidationError({
                "message": f"Order is already {new_status}."
            })

        order.status = new_status

        if new_status == Order.Status.DELIVERED:
            order.delivered_at = timezone.now()
        else:
            order.delivered_at = None

        if new_status == Order.Status.CANCELLED:
            order.cancelled_at = timezone.now()
        else:
            order.cancelled_at = None

        order.save(update_fields=["status", "delivered_at", "cancelled_at", "updated_at"])
        return order