from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin

from apps.printing.models.print_pricing import (
    PrintPricing,
)

from apps.printing.models.printing_service import (
    PrintingService,
)

from apps.printing.serializers.print_pricing_serializer import (
    PrintPricingSerializer,
)

from apps.printing.serializers.printing_service_serializer import (
    PrintingServiceSerializer,
)

from apps.printing.serializers.print_order_serializer import (
    PrintOrderSerializer,
    UpdatePrintOrderStatusSerializer,
)

from apps.printing.services.print_order_service import (
    PrintOrderService,
)


# =========================================================
# ADMIN ORDERS
# =========================================================

@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_print_orders(request):

    orders = PrintOrderService.get_all_orders()

    serializer = PrintOrderSerializer(
        orders,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "All print orders fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_print_order(
    request,
    order_id,
):

    orders = PrintOrderService.get_all_orders()

    order = orders.filter(
        id=order_id
    ).first()

    if not order:
        return Response(
            {
                "success": False,
                "message": "Print order not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = PrintOrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Print order fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def admin_update_print_order_status(
    request,
    order_id,
):

    serializer = UpdatePrintOrderStatusSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    order = PrintOrderService.update_order_status(
        order_id=order_id,
        new_status=serializer.validated_data["status"],
    )

    response_serializer = PrintOrderSerializer(
        order
    )

    return Response(
        {
            "success": True,
            "message": "Print order status updated successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# =========================================================
# ADMIN SERVICES
# =========================================================

@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_printing_services(request):

    services = PrintingService.objects.all()

    serializer = PrintingServiceSerializer(
        services,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Printing services fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAdmin])
def admin_create_printing_service(request):

    serializer = PrintingServiceSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    service = serializer.save()

    response_serializer = PrintingServiceSerializer(
        service
    )

    return Response(
        {
            "success": True,
            "message": "Printing service created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def admin_update_printing_service(
    request,
    service_id,
):

    try:
        service = PrintingService.objects.get(
            id=service_id
        )
    except PrintingService.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Printing service not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = PrintingServiceSerializer(
        service,
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True
    )

    service = serializer.save()

    return Response(
        {
            "success": True,
            "message": "Printing service updated successfully.",
            "data": PrintingServiceSerializer(service).data,
        },
        status=status.HTTP_200_OK,
    )


# =========================================================
# ADMIN PRICING
# =========================================================

@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_printing_pricing(request):

    pricing = (
        PrintPricing.objects
        .select_related("service")
        .order_by("-created_at")
    )

    serializer = PrintPricingSerializer(
        pricing,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Printing pricing fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAdmin])
def admin_create_printing_pricing(request):

    serializer = PrintPricingSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    pricing = serializer.save()

    return Response(
        {
            "success": True,
            "message": "Printing pricing created successfully.",
            "data": PrintPricingSerializer(pricing).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def admin_update_printing_pricing(
    request,
    pricing_id,
):

    try:
        pricing = PrintPricing.objects.get(
            id=pricing_id
        )
    except PrintPricing.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Printing pricing not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = PrintPricingSerializer(
        pricing,
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True
    )

    pricing = serializer.save()

    return Response(
        {
            "success": True,
            "message": "Printing pricing updated successfully.",
            "data": PrintPricingSerializer(pricing).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def admin_delete_printing_pricing(
    request,
    pricing_id,
):

    try:
        pricing = PrintPricing.objects.get(
            id=pricing_id
        )
    except PrintPricing.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Printing pricing not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    pricing.is_active = False

    pricing.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    return Response(
        {
            "success": True,
            "message": "Printing pricing deactivated successfully.",
        },
        status=status.HTTP_200_OK,
    )