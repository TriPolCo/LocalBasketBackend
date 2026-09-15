from django.db.models import Q
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.banner.models.banner import Banner
from apps.banner.serializers.banner_serializer import (
    BannerCreateSerializer,
    BannerSerializer,
)


# ============================================================
# ADMIN - CREATE BANNER
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_banner(request):

    if (
        request.user.role != "ADMIN"
        or not request.user.is_staff
    ):
        return Response(
            {
                "success": False,
                "message": "You are not authorized to create banners.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = BannerCreateSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "message": "Invalid banner data.",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    banner = serializer.save()

    response_serializer = BannerSerializer(
        banner
    )

    return Response(
        {
            "success": True,
            "message": "Banner created successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# APP - FETCH BANNERS
# ============================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def get_banners(request):

    section = request.query_params.get("section")

    now = timezone.now()

    banners = (
        Banner.objects
        .filter(is_active=True)
        .filter(
            Q(start_at__isnull=True) |
            Q(start_at__lte=now)
        )
        .filter(
            Q(end_at__isnull=True) |
            Q(end_at__gte=now)
        )
        .prefetch_related("buttons")
        .order_by(
            "display_order",
            "-created_at",
        )
    )

    # --------------------------------------------------------
    # Optional section filter
    # --------------------------------------------------------

    if section:
        banners = banners.filter(
            section=section.upper()
        )

    serializer = BannerSerializer(
        banners,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Banners fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )