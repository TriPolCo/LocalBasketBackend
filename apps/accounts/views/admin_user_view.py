from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin
from apps.accounts.serializers.admin_user_serializer import (
    AdminUserSerializer,
)
from apps.accounts.services.admin_user_service import (
    AdminUserService,
)


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_get_all_users(request):

    users = AdminUserService.get_all_users()

    serializer = AdminUserSerializer(
        users,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "All users fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )