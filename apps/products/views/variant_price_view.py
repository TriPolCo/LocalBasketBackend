from decimal import Decimal, InvalidOperation

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.products.models import ProductVariant


def _to_decimal(value, field_name):
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid numeric value for {field_name}.")
    if dec < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return dec


@api_view(["PATCH", "PUT"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_variant_price(request, variant_id):
    if getattr(request.user, "role", None) != "ADMIN" and not request.user.is_staff:
        return Response(
            {
                "success": False,
                "message": "Only admins can update product prices.",
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        variant = ProductVariant.objects.select_for_update().get(id=variant_id)
    except ProductVariant.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Product variant not found.",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    data = request.data
    updated_fields = []

    try:
        # Update MRP
        raw_mrp = data.get("mrp")
        if raw_mrp is not None and raw_mrp != "":
            variant.mrp = _to_decimal(raw_mrp, "mrp")
            updated_fields.append("mrp")

        # Update Selling Price
        raw_selling = data.get("selling_price", data.get("price"))
        if raw_selling is not None and raw_selling != "":
            variant.selling_price = _to_decimal(raw_selling, "selling_price")
            updated_fields.append("selling_price")

        # Validate MRP >= Selling Price
        if variant.mrp < variant.selling_price:
            return Response(
                {
                    "success": False,
                    "message": "MRP cannot be less than selling price.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update Stock (accepts "stock" or "stock_quantity")
        raw_stock = data.get("stock", data.get("stock_quantity"))
        if raw_stock is not None and raw_stock != "":
            stock_val = int(raw_stock)
            if stock_val < 0:
                raise ValueError("Stock cannot be negative.")
            variant.stock = stock_val
            updated_fields.append("stock")

        # Optional Active Toggle
        if "is_active" in data:
            variant.is_active = bool(data["is_active"])
            updated_fields.append("is_active")

    except ValueError as err:
        return Response(
            {
                "success": False,
                "message": str(err),
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not updated_fields:
        return Response(
            {
                "success": False,
                "message": "No valid price or stock fields provided.",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    updated_fields.append("updated_at")
    variant.save(update_fields=updated_fields)

    return Response(
        {
            "success": True,
            "message": "Variant price updated successfully.",
            "data": {
                "id": str(variant.id),
                "sku": variant.sku,
                "mrp": float(variant.mrp),
                "selling_price": float(variant.selling_price),
                "stock": variant.stock,
                "is_active": variant.is_active,
            },
        },
        status=status.HTTP_200_OK,
    )