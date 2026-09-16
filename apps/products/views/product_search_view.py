from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.products.serializers.product_search_serializer import (
    ProductSearchSerializer,
)

from apps.products.services.product_search_service import (
    ProductSearchService,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_products(request):

    search = request.query_params.get(
        "search",
        "",
    ).strip()

    if not search:
        return Response(
            {
                "success": False,
                "message": "Search keyword is required.",
                "data": [],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    products = ProductSearchService.search_products(
        search
    )

    serializer = ProductSearchSerializer(
        products,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Products searched successfully.",
            "search": search,
            "count": products.count(),
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )