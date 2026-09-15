from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.accounts.serializers.admin_auth_serializer import (
    AdminLoginSerializer,
)
from apps.accounts.services.admin_auth_service import (
    admin_login,
)


logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login_view(request):
    serializer = AdminLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = admin_login(**serializer.validated_data)
        user = result["user"]
        return Response(
            {
                "message": "Admin login successful.",
                "data": {
                    "user": {
                        "id": str(user.id),
                        "phone_number": user.phone_number,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                    },
                    "tokens": {
                        "access": result["access"],
                        "refresh": result["refresh"],
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as exc:
        return Response(
            {"message": str(exc),},
            status=status.HTTP_401_UNAUTHORIZED,
        )