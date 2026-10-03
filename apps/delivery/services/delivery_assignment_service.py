from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models.delivery_partner import DeliveryPartner
from apps.delivery.models.delivery_assignment import DeliveryAssignment
from apps.food.models.food_order import FoodOrder
from apps.orders.models.order import Order


class DeliveryAssignmentService:

    # ==========================================================
    # ASSIGN NORMAL ORDER
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def assign_order(
        order_id,
        delivery_partner_id,
    ):
        # ------------------------------------------------------
        # Get Order
        # ------------------------------------------------------

        try:
            order = (
                Order.objects
                .select_for_update()
                .get(
                    id=order_id
                )
            )

        except Order.DoesNotExist:
            raise ValidationError({
                "order": "Order not found."
            })

        # ------------------------------------------------------
        # Validate Order Status
        # ------------------------------------------------------

        if order.status in [
            Order.Status.CANCELLED,
            Order.Status.DELIVERED,
        ]:
            raise ValidationError({
                "order": (
                    "Delivery cannot be assigned "
                    "to this order."
                )
            })

        # ------------------------------------------------------
        # Get Delivery Partner
        # ------------------------------------------------------

        try:
            delivery_partner = (
                DeliveryPartner.objects
                .select_related("user")
                .select_for_update()
                .get(
                    id=delivery_partner_id
                )
            )

        except DeliveryPartner.DoesNotExist:
            raise ValidationError({
                "delivery_partner":
                    "Delivery partner not found."
            })

        # ------------------------------------------------------
        # Partner must be active
        # ------------------------------------------------------

        if not delivery_partner.user.is_active:
            raise ValidationError({
                "delivery_partner":
                    "Delivery partner account is inactive."
            })

        # ------------------------------------------------------
        # Check existing assignment
        # ------------------------------------------------------

        existing_assignment = (
            DeliveryAssignment.objects
            .filter(
                order=order
            )
            .first()
        )

        if existing_assignment:
            raise ValidationError({
                "order":
                    "This order is already assigned."
            })

        # ------------------------------------------------------
        # Create Assignment
        # ------------------------------------------------------

        assignment = (
            DeliveryAssignment.objects.create(
                order=order,
                delivery_partner=delivery_partner,
                status=(
                    DeliveryAssignment
                    .Status
                    .ASSIGNED
                ),
            )
        )

        return assignment

    # ==========================================================
    # ASSIGN FOOD ORDER
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def assign_food_order(
        food_order_id,
        delivery_partner_id,
    ):
        # ------------------------------------------------------
        # Get Food Order
        # ------------------------------------------------------

        try:
            food_order = (
                FoodOrder.objects
                .select_for_update()
                .get(
                    id=food_order_id
                )
            )

        except FoodOrder.DoesNotExist:
            raise ValidationError({
                "food_order": "Food order not found."
            })

        # ------------------------------------------------------
        # Validate Order Status
        # ------------------------------------------------------

        if food_order.status in [
            FoodOrder.Status.CANCELLED,
            FoodOrder.Status.DELIVERED,
        ]:
            raise ValidationError({
                "food_order": (
                    "Delivery cannot be assigned "
                    "to this order."
                )
            })

        # ------------------------------------------------------
        # Get Delivery Partner
        # ------------------------------------------------------

        try:
            delivery_partner = (
                DeliveryPartner.objects
                .select_related("user")
                .select_for_update()
                .get(
                    id=delivery_partner_id
                )
            )

        except DeliveryPartner.DoesNotExist:
            raise ValidationError({
                "delivery_partner":
                    "Delivery partner not found."
            })

        # ------------------------------------------------------
        # Partner must be active
        # ------------------------------------------------------

        if not delivery_partner.user.is_active:
            raise ValidationError({
                "delivery_partner":
                    "Delivery partner account is inactive."
            })

        # ------------------------------------------------------
        # Check existing assignment
        # ------------------------------------------------------

        existing_assignment = (
            DeliveryAssignment.objects
            .filter(
                food_order=food_order
            )
            .first()
        )

        if existing_assignment:
            raise ValidationError({
                "food_order":
                    "This food order is already assigned."
            })

        # ------------------------------------------------------
        # Create Assignment
        # ------------------------------------------------------

        assignment = (
            DeliveryAssignment.objects.create(
                food_order=food_order,
                delivery_partner=delivery_partner,
                status=(
                    DeliveryAssignment
                    .Status
                    .ASSIGNED
                ),
            )
        )

        return assignment

    # ==========================================================
    # GET NORMAL ORDER ASSIGNMENT
    # ==========================================================

    @staticmethod
    def get_order_assignment(order_id):
        try:
            return (
                DeliveryAssignment.objects
                .select_related(
                    "delivery_partner",
                    "delivery_partner__user",
                    "order",
                )
                .get(
                    order_id=order_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

    # ==========================================================
    # GET FOOD ORDER ASSIGNMENT
    # ==========================================================

    @staticmethod
    def get_food_order_assignment(food_order_id):
        try:
            return (
                DeliveryAssignment.objects
                .select_related(
                    "delivery_partner",
                    "delivery_partner__user",
                    "food_order",
                )
                .get(
                    food_order_id=food_order_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

    # ==========================================================
    # GET ASSIGNMENT
    # ==========================================================

    @staticmethod
    def get_assignment(assignment_id):
        try:
            return (
                DeliveryAssignment.objects
                .select_related(
                    "delivery_partner",
                    "delivery_partner__user",
                    "order",
                    "food_order",
                )
                .get(
                    id=assignment_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

    # ==========================================================
    # ACCEPT ASSIGNMENT
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def accept_assignment(
        assignment_id,
        delivery_partner_id,
    ):
        try:
            assignment = (
                DeliveryAssignment.objects
                .select_for_update()
                .select_related(
                    "delivery_partner",
                    "order",
                    "food_order",
                )
                .get(
                    id=assignment_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

        # ------------------------------------------------------
        # Verify Partner
        # ------------------------------------------------------

        if str(
            assignment.delivery_partner.id
        ) != str(delivery_partner_id):
            raise ValidationError({
                "assignment":
                    "You are not assigned to this delivery."
            })

        # ------------------------------------------------------
        # Validate Status
        # ------------------------------------------------------

        if assignment.status != (
            DeliveryAssignment
            .Status
            .ASSIGNED
        ):
            raise ValidationError({
                "status":
                    "This assignment cannot be accepted."
            })

        # ------------------------------------------------------
        # Accept
        # ------------------------------------------------------

        assignment.status = (
            DeliveryAssignment
            .Status
            .ACCEPTED
        )

        assignment.accepted_at = timezone.now()

        assignment.save(
            update_fields=[
                "status",
                "accepted_at",
                "updated_at",
            ]
        )

        return assignment

    # ==========================================================
    # START DELIVERY
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def start_delivery(
        assignment_id,
        delivery_partner_id,
    ):
        try:
            assignment = (
                DeliveryAssignment.objects
                .select_for_update()
                .select_related(
                    "delivery_partner",
                    "order",
                    "food_order",
                )
                .get(
                    id=assignment_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

        # ------------------------------------------------------
        # Verify Partner
        # ------------------------------------------------------

        if str(
            assignment.delivery_partner.id
        ) != str(delivery_partner_id):
            raise ValidationError({
                "assignment":
                    "You are not assigned to this delivery."
            })

        # ------------------------------------------------------
        # Validate Status
        # ------------------------------------------------------

        if assignment.status != (
            DeliveryAssignment
            .Status
            .ACCEPTED
        ):
            raise ValidationError({
                "status":
                    "Delivery must be accepted before starting."
            })

        # ------------------------------------------------------
        # Start Delivery
        # ------------------------------------------------------

        assignment.status = (
            DeliveryAssignment
            .Status
            .IN_TRANSIT
        )

        assignment.started_at = timezone.now()

        assignment.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

        return assignment

    # ==========================================================
    # COMPLETE DELIVERY
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def complete_delivery(
        assignment_id,
        delivery_partner_id,
    ):
        try:
            assignment = (
                DeliveryAssignment.objects
                .select_for_update()
                .select_related(
                    "delivery_partner",
                    "order",
                    "food_order",
                )
                .get(
                    id=assignment_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

        # ------------------------------------------------------
        # Verify Partner
        # ------------------------------------------------------

        if str(
            assignment.delivery_partner.id
        ) != str(delivery_partner_id):
            raise ValidationError({
                "assignment":
                    "You are not assigned to this delivery."
            })

        # ------------------------------------------------------
        # Validate Status
        # ------------------------------------------------------

        if assignment.status != (
            DeliveryAssignment
            .Status
            .IN_TRANSIT
        ):
            raise ValidationError({
                "status":
                    "Delivery must be in transit before completion."
            })

        # ------------------------------------------------------
        # Complete Assignment
        # ------------------------------------------------------

        assignment.status = (
            DeliveryAssignment
            .Status
            .DELIVERED
        )

        assignment.delivered_at = timezone.now()

        assignment.save(
            update_fields=[
                "status",
                "delivered_at",
                "updated_at",
            ]
        )

        # ------------------------------------------------------
        # Update Normal Order
        # ------------------------------------------------------

        if assignment.order_id:
            order = (
                Order.objects
                .select_for_update()
                .get(
                    id=assignment.order_id
                )
            )

            if order.status != Order.Status.CANCELLED:
                order.status = Order.Status.DELIVERED
                order.delivered_at = timezone.now()

                order.save(
                    update_fields=[
                        "status",
                        "delivered_at",
                        "updated_at",
                    ]
                )

        # ------------------------------------------------------
        # Update Food Order
        # ------------------------------------------------------

        if assignment.food_order_id:
            food_order = (
                FoodOrder.objects
                .select_for_update()
                .get(
                    id=assignment.food_order_id
                )
            )

            if food_order.status != FoodOrder.Status.CANCELLED:
                food_order.status = (
                    FoodOrder.Status.DELIVERED
                )

                food_order.delivered_at = timezone.now()

                food_order.save(
                    update_fields=[
                        "status",
                        "delivered_at",
                        "updated_at",
                    ]
                )

        return assignment

    # ==========================================================
    # UPLOAD DELIVERY PROOF
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def upload_delivery_proof(
        assignment_id,
        delivery_partner_id,
        delivery_image_url,
        delivery_image_public_id,
        payment_method,
        payment_confirmed=False,
    ):
        try:
            assignment = (
                DeliveryAssignment.objects
                .select_for_update()
                .select_related(
                    "delivery_partner",
                    "order",
                    "food_order",
                )
                .get(
                    id=assignment_id
                )
            )

        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment":
                    "Delivery assignment not found."
            })

        # ------------------------------------------------------
        # Verify Partner
        # ------------------------------------------------------

        if str(
            assignment.delivery_partner.id
        ) != str(delivery_partner_id):
            raise ValidationError({
                "assignment":
                    "You are not assigned to this delivery."
            })

        # ------------------------------------------------------
        # Validate Status
        # ------------------------------------------------------

        if assignment.status not in [
            DeliveryAssignment.Status.IN_TRANSIT,
            DeliveryAssignment.Status.DELIVERED,
        ]:
            raise ValidationError({
                "status":
                    "Delivery proof cannot be uploaded at this stage."
            })

        # ------------------------------------------------------
        # Save Proof
        # ------------------------------------------------------

        assignment.delivery_image_url = delivery_image_url

        assignment.delivery_image_public_id = (
            delivery_image_public_id
        )

        assignment.payment_method = payment_method

        assignment.payment_confirmed = (
            payment_confirmed
        )

        assignment.save(
            update_fields=[
                "delivery_image_url",
                "delivery_image_public_id",
                "payment_method",
                "payment_confirmed",
                "updated_at",
            ]
        )

        return assignment