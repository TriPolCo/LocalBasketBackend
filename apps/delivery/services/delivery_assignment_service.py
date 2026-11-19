import uuid
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models.delivery_partner import DeliveryPartner
from apps.delivery.models.delivery_assignment import DeliveryAssignment
from apps.food.models.food_order import FoodOrder
from apps.orders.models.order import Order


class DeliveryAssignmentService:

    ACTIVE_STATUSES = [
        DeliveryAssignment.Status.ASSIGNED,
        DeliveryAssignment.Status.ACCEPTED,
        DeliveryAssignment.Status.IN_TRANSIT,
    ]

    HISTORY_STATUSES = [
        DeliveryAssignment.Status.DELIVERED,
        DeliveryAssignment.Status.CANCELLED,
    ]

    @staticmethod
    def _base_queryset():
        return DeliveryAssignment.objects.select_related(
            "delivery_partner",
            "delivery_partner__user",
            "order",
            "order__customer",
            "order__shipping_address",
            "food_order",
        )

    @staticmethod
    def _mark_linked_order_delivered(assignment):
        now = timezone.now()

        if assignment.order_id:
            order = (
                Order.objects
                .select_for_update()
                .get(id=assignment.order_id)
            )
            if order.status != Order.Status.CANCELLED:
                order.status = Order.Status.DELIVERED
                order.delivered_at = now
                order.save(
                    update_fields=[
                        "status",
                        "delivered_at",
                        "updated_at",
                    ]
                )

        if assignment.food_order_id:
            food_order = (
                FoodOrder.objects
                .select_for_update()
                .get(id=assignment.food_order_id)
            )
            if food_order.status != FoodOrder.Status.CANCELLED:
                food_order.status = FoodOrder.Status.DELIVERED
                food_order.delivered_at = now
                food_order.save(
                    update_fields=[
                        "status",
                        "delivered_at",
                        "updated_at",
                    ]
                )

    # ==========================================================
    # ASSIGN NORMAL ORDER
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def assign_order(
        order_id,
        delivery_partner_id,
    ):
        try:
            order = (
                Order.objects
                .select_for_update()
                .get(id=order_id)
            )
        except Order.DoesNotExist:
            raise ValidationError({
                "order": "Order not found."
            })

        if order.status in [
            Order.Status.CANCELLED,
            Order.Status.DELIVERED,
        ]:
            raise ValidationError({
                "order": "Delivery cannot be assigned to this order."
            })

        try:
            delivery_partner = (
                DeliveryPartner.objects
                .select_related("user")
                .select_for_update()
                .get(id=delivery_partner_id)
            )
        except DeliveryPartner.DoesNotExist:
            raise ValidationError({
                "delivery_partner": "Delivery partner not found."
            })

        if not delivery_partner.user.is_active:
            raise ValidationError({
                "delivery_partner": "Delivery partner account is inactive."
            })

        if DeliveryAssignment.objects.filter(order=order).exists():
            raise ValidationError({
                "order": "This order is already assigned."
            })

        return DeliveryAssignment.objects.create(
            order=order,
            delivery_partner=delivery_partner,
            status=DeliveryAssignment.Status.ASSIGNED,
        )

    # ==========================================================
    # ASSIGN FOOD ORDER
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def assign_food_order(
        food_order_id,
        delivery_partner_id,
    ):
        try:
            food_order = (
                FoodOrder.objects
                .select_for_update()
                .get(id=food_order_id)
            )
        except FoodOrder.DoesNotExist:
            raise ValidationError({
                "food_order": "Food order not found."
            })

        if food_order.status in [
            FoodOrder.Status.CANCELLED,
            FoodOrder.Status.DELIVERED,
        ]:
            raise ValidationError({
                "food_order": "Delivery cannot be assigned to this order."
            })

        try:
            delivery_partner = (
                DeliveryPartner.objects
                .select_related("user")
                .select_for_update()
                .get(id=delivery_partner_id)
            )
        except DeliveryPartner.DoesNotExist:
            raise ValidationError({
                "delivery_partner": "Delivery partner not found."
            })

        if not delivery_partner.user.is_active:
            raise ValidationError({
                "delivery_partner": "Delivery partner account is inactive."
            })

        if DeliveryAssignment.objects.filter(food_order=food_order).exists():
            raise ValidationError({
                "food_order": "This food order is already assigned."
            })

        return DeliveryAssignment.objects.create(
            food_order=food_order,
            delivery_partner=delivery_partner,
            status=DeliveryAssignment.Status.ASSIGNED,
        )

    # ==========================================================
    # GET ALL ASSIGNMENTS (ADMIN)
    # ==========================================================

    @staticmethod
    def get_assignments(status_filter=None):
        queryset = DeliveryAssignmentService._base_queryset()
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return queryset.order_by("-assigned_at")

    # ==========================================================
    # GET PARTNER ASSIGNMENTS (DELIVERY PARTNER APP)
    # ==========================================================

    @staticmethod
    def get_partner_assignments(
        delivery_partner,
        scope=None,
    ):
        queryset = DeliveryAssignmentService._base_queryset().filter(
            delivery_partner=delivery_partner
        )

        if scope:
            scope_upper = scope.strip().upper()
            if scope_upper == "ACTIVE":
                queryset = queryset.filter(
                    status__in=DeliveryAssignmentService.ACTIVE_STATUSES
                )
            elif scope_upper == "HISTORY":
                queryset = queryset.filter(
                    status__in=DeliveryAssignmentService.HISTORY_STATUSES
                )
            elif scope_upper in DeliveryAssignment.Status.values:
                queryset = queryset.filter(status=scope_upper)

        return queryset.order_by("-assigned_at")

    # ==========================================================
    # SCAN / LOOKUP PARTNER ASSIGNMENT BY QR OR ORDER CODE
    # ==========================================================

    @staticmethod
    def find_partner_assignment_by_code(
        delivery_partner,
        raw_code,
    ):
        code = (raw_code or "").strip()
        if not code:
            raise ValidationError({"code": "Scanned code is empty."})

        queryset = DeliveryAssignmentService._base_queryset().filter(
            delivery_partner=delivery_partner
        )

        # 1. Try UUID match (assignment_id, order_id, or food_order_id)
        try:
            parsed_uuid = uuid.UUID(code)
            assignment = (
                queryset.filter(id=parsed_uuid).first()
                or queryset.filter(order_id=parsed_uuid).first()
                or queryset.filter(food_order_id=parsed_uuid).first()
            )
            if assignment:
                return assignment
        except ValueError:
            pass

        # 2. Try matching order_number (e.g. ORD-1024)
        for item in queryset:
            target = item.order or item.food_order
            order_number = getattr(target, "order_number", None)
            if order_number and str(order_number).strip().upper() == code.upper():
                return item

        raise ValidationError({
            "assignment": "No assigned delivery matched this scanned code."
        })

    # ==========================================================
    # GET NORMAL ORDER ASSIGNMENT
    # ==========================================================

    @staticmethod
    def get_order_assignment(order_id):
        try:
            return DeliveryAssignmentService._base_queryset().get(
                order_id=order_id
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
            })

    # ==========================================================
    # GET FOOD ORDER ASSIGNMENT
    # ==========================================================

    @staticmethod
    def get_food_order_assignment(food_order_id):
        try:
            return DeliveryAssignmentService._base_queryset().get(
                food_order_id=food_order_id
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
            })

    # ==========================================================
    # GET ASSIGNMENT
    # ==========================================================

    @staticmethod
    def get_assignment(assignment_id):
        try:
            return DeliveryAssignmentService._base_queryset().get(
                id=assignment_id
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
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
                DeliveryAssignmentService._base_queryset()
                .select_for_update()
                .get(id=assignment_id)
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
            })

        if str(assignment.delivery_partner.id) != str(delivery_partner_id):
            raise ValidationError({
                "assignment": "You are not assigned to this delivery."
            })

        if assignment.status != DeliveryAssignment.Status.ASSIGNED:
            raise ValidationError({
                "status": "This assignment cannot be accepted."
            })

        assignment.status = DeliveryAssignment.Status.ACCEPTED
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
                DeliveryAssignmentService._base_queryset()
                .select_for_update()
                .get(id=assignment_id)
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
            })

        if str(assignment.delivery_partner.id) != str(delivery_partner_id):
            raise ValidationError({
                "assignment": "You are not assigned to this delivery."
            })

        if assignment.status != DeliveryAssignment.Status.ACCEPTED:
            raise ValidationError({
                "status": "Delivery must be accepted before starting."
            })

        assignment.status = DeliveryAssignment.Status.IN_TRANSIT
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
                DeliveryAssignmentService._base_queryset()
                .select_for_update()
                .get(id=assignment_id)
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
            })

        if str(assignment.delivery_partner.id) != str(delivery_partner_id):
            raise ValidationError({
                "assignment": "You are not assigned to this delivery."
            })

        if assignment.status != DeliveryAssignment.Status.IN_TRANSIT:
            raise ValidationError({
                "status": "Delivery must be in transit before completion."
            })

        assignment.status = DeliveryAssignment.Status.DELIVERED
        assignment.delivered_at = timezone.now()
        assignment.save(
            update_fields=[
                "status",
                "delivered_at",
                "updated_at",
            ]
        )

        DeliveryAssignmentService._mark_linked_order_delivered(assignment)
        return assignment

    # ==========================================================
    # UPLOAD DELIVERY PROOF (AND MARK DELIVERED)
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
                DeliveryAssignmentService._base_queryset()
                .select_for_update()
                .get(id=assignment_id)
            )
        except DeliveryAssignment.DoesNotExist:
            raise ValidationError({
                "assignment": "Delivery assignment not found."
            })

        if str(assignment.delivery_partner.id) != str(delivery_partner_id):
            raise ValidationError({
                "assignment": "You are not assigned to this delivery."
            })

        if assignment.status not in [
            DeliveryAssignment.Status.IN_TRANSIT,
            DeliveryAssignment.Status.DELIVERED,
        ]:
            raise ValidationError({
                "status": "Delivery proof can only be uploaded when in transit or delivered."
            })

        assignment.delivery_image_url = delivery_image_url
        assignment.delivery_image_public_id = delivery_image_public_id
        assignment.payment_method = payment_method
        assignment.payment_confirmed = payment_confirmed

        update_fields = [
            "delivery_image_url",
            "delivery_image_public_id",
            "payment_method",
            "payment_confirmed",
            "updated_at",
        ]

        if assignment.status == DeliveryAssignment.Status.IN_TRANSIT:
            assignment.status = DeliveryAssignment.Status.DELIVERED
            assignment.delivered_at = timezone.now()
            update_fields.extend(["status", "delivered_at"])

        assignment.save(update_fields=update_fields)

        if assignment.status == DeliveryAssignment.Status.DELIVERED:
            DeliveryAssignmentService._mark_linked_order_delivered(assignment)

        return assignment