from rest_framework import serializers

from apps.banner.models.banner import Banner
from apps.banner.models.banner_button import BannerButton


# ============================================================
# BANNER BUTTON RESPONSE SERIALIZER
# ============================================================

class BannerButtonSerializer(serializers.ModelSerializer):

    navigation = serializers.SerializerMethodField()

    class Meta:
        model = BannerButton

        fields = [
            "id",
            "label",
            "navigation",
            "display_order",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]

    def get_navigation(self, obj):

        if obj.navigation_type == BannerButton.NavigationType.URL:
            return {
                "type": obj.navigation_type,
                "url": obj.navigation_url,
            }

        if obj.navigation_type == BannerButton.NavigationType.NONE:
            return {
                "type": obj.navigation_type,
            }

        return {
            "type": obj.navigation_type,
            "id": str(obj.navigation_id)
            if obj.navigation_id
            else None,
        }


# ============================================================
# BANNER RESPONSE SERIALIZER
# ============================================================

class BannerSerializer(serializers.ModelSerializer):

    navigation = serializers.SerializerMethodField()
    buttons = serializers.SerializerMethodField()

    class Meta:
        model = Banner

        fields = [
            "id",
            "title",
            "subtitle",
            "image_url",
            "mobile_image_url",
            "section",
            "navigation",
            "buttons",
            "display_order",
            "is_active",
            "start_at",
            "end_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "navigation",
            "buttons",
            "created_at",
            "updated_at",
        ]

    def get_navigation(self, obj):

        if obj.navigation_type == Banner.NavigationType.URL:
            return {
                "type": obj.navigation_type,
                "url": obj.navigation_url,
            }

        if obj.navigation_type == Banner.NavigationType.NONE:
            return {
                "type": obj.navigation_type,
            }

        return {
            "type": obj.navigation_type,
            "id": str(obj.navigation_id)
            if obj.navigation_id
            else None,
        }

    def get_buttons(self, obj):

        buttons = obj.buttons.filter(
            is_active=True
        ).order_by(
            "display_order",
            "created_at",
        )

        return BannerButtonSerializer(
            buttons,
            many=True,
        ).data


# ============================================================
# BANNER BUTTON CREATE SERIALIZER
# ============================================================

class BannerButtonCreateSerializer(serializers.Serializer):

    label = serializers.CharField(
        max_length=50
    )

    navigation_type = serializers.ChoiceField(
        choices=BannerButton.NavigationType.choices,
        default=BannerButton.NavigationType.NONE,
    )

    navigation_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    navigation_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    is_active = serializers.BooleanField(
        required=False,
        default=True,
    )

    def validate(self, attrs):

        navigation_type = attrs.get("navigation_type")
        navigation_id = attrs.get("navigation_id")
        navigation_url = attrs.get("navigation_url")

        if navigation_type == BannerButton.NavigationType.URL:

            if not navigation_url:
                raise serializers.ValidationError({
                    "navigation_url": (
                        "navigation_url is required "
                        "for URL navigation."
                    )
                })

            attrs["navigation_id"] = None

        elif navigation_type != BannerButton.NavigationType.NONE:

            if not navigation_id:
                raise serializers.ValidationError({
                    "navigation_id": (
                        "navigation_id is required "
                        "for this navigation type."
                    )
                })

            attrs["navigation_url"] = None

        else:

            attrs["navigation_id"] = None
            attrs["navigation_url"] = None

        return attrs


# ============================================================
# BANNER CREATE SERIALIZER
# ============================================================

class BannerCreateSerializer(serializers.Serializer):

    title = serializers.CharField(
        max_length=200
    )

    subtitle = serializers.CharField(
        max_length=300,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    image_url = serializers.URLField(
        max_length=1000
    )

    image_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    mobile_image_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    mobile_image_public_id = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    section = serializers.ChoiceField(
        choices=Banner.Section.choices
    )

    navigation_type = serializers.ChoiceField(
        choices=Banner.NavigationType.choices,
        default=Banner.NavigationType.NONE,
    )

    navigation_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    navigation_url = serializers.URLField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    display_order = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    is_active = serializers.BooleanField(
        required=False,
        default=True,
    )

    start_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    end_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    buttons = BannerButtonCreateSerializer(
        many=True,
        required=False,
        default=list,
    )

    # ========================================================
    # TITLE
    # ========================================================

    def validate_title(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Banner title cannot be empty."
            )

        return value

    # ========================================================
    # VALIDATE
    # ========================================================

    def validate(self, attrs):

        navigation_type = attrs.get("navigation_type")
        navigation_id = attrs.get("navigation_id")
        navigation_url = attrs.get("navigation_url")

        start_at = attrs.get("start_at")
        end_at = attrs.get("end_at")

        # ----------------------------------------------------
        # URL navigation
        # ----------------------------------------------------

        if navigation_type == Banner.NavigationType.URL:

            if not navigation_url:
                raise serializers.ValidationError({
                    "navigation_url": (
                        "navigation_url is required "
                        "for URL navigation."
                    )
                })

            attrs["navigation_id"] = None

        # ----------------------------------------------------
        # Internal navigation
        # ----------------------------------------------------

        elif navigation_type != Banner.NavigationType.NONE:

            if not navigation_id:
                raise serializers.ValidationError({
                    "navigation_id": (
                        "navigation_id is required "
                        "for this navigation type."
                    )
                })

            attrs["navigation_url"] = None

        # ----------------------------------------------------
        # No navigation
        # ----------------------------------------------------

        else:

            attrs["navigation_id"] = None
            attrs["navigation_url"] = None

        # ----------------------------------------------------
        # Date validation
        # ----------------------------------------------------

        if start_at and end_at:

            if end_at <= start_at:
                raise serializers.ValidationError({
                    "end_at": (
                        "End time must be greater than "
                        "start time."
                    )
                })

        return attrs

    # ========================================================
    # CREATE
    # ========================================================

    def create(self, validated_data):

        buttons_data = validated_data.pop(
            "buttons",
            []
        )

        banner = Banner.objects.create(
            **validated_data
        )

        for button_data in buttons_data:

            BannerButton.objects.create(
                banner=banner,
                **button_data
            )

        return banner