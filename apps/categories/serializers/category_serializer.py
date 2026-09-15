from django.utils.text import slugify
from rest_framework import serializers

from apps.categories.models.category import Category


class CategoryListSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(
        read_only=True,
    )

    subcategory_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "is_active",
            "product_count",
            "subcategory_count",
            "created_at",
            "updated_at",
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "is_active",
            "product_count",
            "created_at",
            "updated_at",
        ]


class MainCategoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "name",
            "is_active",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Category name is required."
            )

        if Category.objects.filter(
            name__iexact=value,
            parent__isnull=True,
        ).exists():
            raise serializers.ValidationError(
                "A main category with this name already exists."
            )

        return value

    def create(self, validated_data):
        validated_data["slug"] = slugify(
            validated_data["name"]
        )

        return Category.objects.create(
            parent=None,
            **validated_data,
        )


class SubcategoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "name",
            "is_active",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Subcategory name is required."
            )

        parent = self.context.get("parent")

        if not parent:
            raise serializers.ValidationError(
                "Parent category is required."
            )

        if Category.objects.filter(
            parent=parent,
            name__iexact=value,
        ).exists():
            raise serializers.ValidationError(
                "This subcategory already exists."
            )

        return value

    def create(self, validated_data):
        parent = self.context["parent"]

        validated_data["slug"] = slugify(
            f"{parent.name}-{validated_data['name']}"
        )

        return Category.objects.create(
            parent=parent,
            **validated_data,
        )


class MainCategoryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "name",
            "is_active",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Category name is required."
            )

        category = self.instance

        if Category.objects.filter(
            name__iexact=value,
            parent__isnull=True,
        ).exclude(
            id=category.id
        ).exists():
            raise serializers.ValidationError(
                "A main category with this name already exists."
            )

        return value

    def update(self, instance, validated_data):

        if "name" in validated_data:
            new_name = validated_data["name"]

            if new_name != instance.name:
                instance.slug = slugify(new_name)

        return super().update(
            instance,
            validated_data,
        )


class SubcategoryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "name",
            "is_active",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Subcategory name is required."
            )

        category = self.instance

        if Category.objects.filter(
            parent=category.parent,
            name__iexact=value,
        ).exclude(
            id=category.id
        ).exists():
            raise serializers.ValidationError(
                "This subcategory already exists."
            )

        return value

    def update(self, instance, validated_data):

        if "name" in validated_data:
            new_name = validated_data["name"]

            if new_name != instance.name:
                instance.slug = slugify(
                    f"{instance.parent.name}-{new_name}"
                )

        return super().update(
            instance,
            validated_data,
        )