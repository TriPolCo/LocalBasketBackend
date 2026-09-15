from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.printing.models.printing_service import (
    PrintingService,
)
from apps.printing.models.print_pricing import (
    PrintPricing,
)

from apps.printing.serializers.printing_service_serializer import (
    PrintingServiceSerializer,
)

from apps.printing.serializers.print_pricing_serializer import (
    PrintPricingSerializer,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_printing_services(request):

    services = (
        PrintingService.objects
        .filter(is_active=True)
        .order_by("display_order")
    )

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_printing_pricing(request):

    pricing = (
        PrintPricing.objects
        .filter(
            is_active=True,
            service__is_active=True,
        )
        .select_related("service")
        .order_by(
            "service__display_order",
            "paper_size",
            "color_type",
        )
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