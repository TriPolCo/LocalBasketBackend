from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.address.serializers.address_serializer import (
    AddressCreateSerializer,
    AddressUpdateSerializer,
    AddressSerializer,
)
from apps.address.services.address_service import AddressService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_address(request):

    serializer = AddressCreateSerializer(
        data=request.data
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = request.user.customer_profile

    address = AddressService.create_address(
        customer=customer,
        **serializer.validated_data,
    )

    response_serializer = AddressSerializer(
        address
    )

    return Response(
        {
            "success": True,
            "message": "Address added successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_addresses(request):

    customer = request.user.customer_profile

    addresses = AddressService.get_addresses(
        customer=customer
    )

    serializer = AddressSerializer(
        addresses,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Addresses fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_address(request, address_id):

    customer = request.user.customer_profile

    address = AddressService.get_address(
        customer=customer,
        address_id=address_id,
    )

    serializer = AddressSerializer(address)

    return Response(
        {
            "success": True,
            "message": "Address fetched successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_address(request, address_id):

    serializer = AddressUpdateSerializer(
        data=request.data,
        partial=True,
    )

    serializer.is_valid(
        raise_exception=True
    )

    customer = request.user.customer_profile

    address = AddressService.update_address(
        customer=customer,
        address_id=address_id,
        **serializer.validated_data,
    )

    response_serializer = AddressSerializer(
        address
    )

    return Response(
        {
            "success": True,
            "message": "Address updated successfully.",
            "data": response_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def set_default_address(request, address_id):

    customer = request.user.customer_profile

    address = AddressService.set_default_address(
        customer=customer,
        address_id=address_id,
    )

    serializer = AddressSerializer(address)

    return Response(
        {
            "success": True,
            "message": "Default address updated successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_address(request, address_id):

    customer = request.user.customer_profile

    AddressService.delete_address(
        customer=customer,
        address_id=address_id,
    )

    addresses = AddressService.get_addresses(
        customer=customer
    )

    serializer = AddressSerializer(
        addresses,
        many=True,
    )

    return Response(
        {
            "success": True,
            "message": "Address deleted successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )