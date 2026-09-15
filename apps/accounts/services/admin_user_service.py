from apps.accounts.models.user import User


class AdminUserService:

    @staticmethod
    def get_all_users():
        return (
            User.objects
            .prefetch_related("customer_profile")
            .order_by("-created_at")
        )