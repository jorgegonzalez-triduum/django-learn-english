from rest_framework import permissions
from django.utils import timezone
from platform_settings.models import UserSubscription

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class HasSubscriptionOrIsAdmin(permissions.BasePermission):
    """
    Check if user has an active subscription or if is superadmin,
    Injects user_subscription_instance to the self attributes of the view
    
    :param user_subscription_instance: UserSubscription model instance
    """

    def has_permission(self, request, view):
        view.user_subscription_instance = UserSubscription.objects.filter(
                user=view.request.user,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).last()
        return True if (
            view.user_subscription_instance
            ) or request.user.is_superuser else False