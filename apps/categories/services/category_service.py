from django.db import transaction
from django.db.models import Count
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.categories.models.category import Category


# ============================================================
# GET MAIN CATEGORIES
# ============================================================

def get_main_categories():
    return (
        Category.objects
        .filter(parent__isnull=True)
        .annotate(
            subcategory_count=Count(
                "subcategories",
                distinct=True,
            ),
        )
        .prefetch_related(
            "subcategories",
        )
    )


# ============================================================
# GET SUBCATEGORIES
# ============================================================

def get_subcategories(parent_id):
    return (
        Category.objects
        .filter(parent_id=parent_id)
        .annotate(
            subcategory_count=Count(
                "subcategories",
                distinct=True,
            ),
        )
    )


# ============================================================
# GET SINGLE CATEGORY
# ============================================================

def get_category(category_id):
    try:
        return Category.objects.get(
            id=category_id,
        )

    except Category.DoesNotExist:
        raise ValidationError(
            {
                "message": "Category not found.",
            }
        )


# ============================================================
# CREATE MAIN CATEGORY
# ============================================================

@transaction.atomic
def create_main_category(validated_data):
    name = validated_data["name"]

    validated_data["slug"] = slugify(name)

    return Category.objects.create(
        parent=None,
        **validated_data,
    )


# ============================================================
# CREATE SUBCATEGORY
# ============================================================

@transaction.atomic
def create_subcategory(
    parent,
    validated_data,
):
    if parent.parent_id is not None:
        raise ValidationError(
            {
                "message": (
                    "Subcategories can only be added "
                    "under a main category."
                ),
            }
        )

    name = validated_data["name"]

    validated_data["slug"] = slugify(
        f"{parent.name}-{name}"
    )

    return Category.objects.create(
        parent=parent,
        **validated_data,
    )


# ============================================================
# UPDATE MAIN CATEGORY
# ============================================================

@transaction.atomic
def update_main_category(
    category,
    validated_data,
):
    if category.parent_id is not None:
        raise ValidationError(
            {
                "message": (
                    "This category is a subcategory."
                ),
            }
        )

    if "name" in validated_data:
        new_name = validated_data["name"]

        if new_name != category.name:
            category.slug = slugify(new_name)

    for field, value in validated_data.items():
        setattr(category, field, value)

    category.save()

    return category


# ============================================================
# UPDATE SUBCATEGORY
# ============================================================

@transaction.atomic
def update_subcategory(
    category,
    validated_data,
):
    if category.parent_id is None:
        raise ValidationError(
            {
                "message": (
                    "This category is a main category."
                ),
            }
        )

    if "name" in validated_data:
        new_name = validated_data["name"]

        if new_name != category.name:
            category.slug = slugify(
                f"{category.parent.name}-{new_name}"
            )

    for field, value in validated_data.items():
        setattr(category, field, value)

    category.save()

    return category


# ============================================================
# DELETE CATEGORY / SUBCATEGORY
# ============================================================

@transaction.atomic
def delete_category(category):

    subcategory_count = (
        category.subcategories.count()
    )

    if subcategory_count > 0:
        raise ValidationError(
            {
                "message": (
                    "Category cannot be deleted because "
                    f"{subcategory_count} subcategor"
                    f"{'y' if subcategory_count == 1 else 'ies'} "
                    "exist under this category."
                ),
            }
        )

    # Product model is not created yet.
    # Product count validation will be added later.

    category.delete()


# ============================================================
# GET CATEGORY TREE
# ============================================================

def get_category_tree():

    categories = (
        Category.objects
        .filter(parent__isnull=True)
        .annotate(
            subcategory_count=Count(
                "subcategories",
                distinct=True,
            ),
        )
        .prefetch_related(
            "subcategories",
        )
    )

    result = []

    for category in categories:

        subcategories = (
            category.subcategories
            .all()
        )

        result.append(
            {
                "id": str(category.id),
                "name": category.name,
                "slug": category.slug,
                "is_active": category.is_active,

                # Temporary until Product model exists
                "product_count": 0,

                "subcategory_count": (
                    category.subcategory_count
                ),

                "subcategories": [
                    {
                        "id": str(sub.id),
                        "name": sub.name,
                        "slug": sub.slug,
                        "is_active": sub.is_active,

                        # Temporary until Product model exists
                        "product_count": 0,
                    }
                    for sub in subcategories
                ],
            }
        )

    return result