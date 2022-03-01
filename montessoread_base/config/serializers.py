from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils import timezone
from platform_settings.models import UserSubscription
from platform_settings.serializers import UserSubscriptionSerializer
from triduum_resource.cross_app import serializers as cross_app_serializers

class UserSerializer(cross_app_serializers.UserSerializer):
    
    active_subscription = serializers.SerializerMethodField()

    def get_active_subscription(self, instance):
        active_subscription = {}
        try:
            active_subscription_instance = UserSubscription.objects.get(
                user=instance,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ) 
        except UserSubscription.DoesNotExist:
            active_subscription_instance = None
        if active_subscription_instance:
            active_subscription = UserSubscriptionSerializer(
                instance=active_subscription_instance, context={
                'request': self.context['request']
            }, read_only=True).data
        return active_subscription
        
    
    class Meta(cross_app_serializers.UserSerializer):
        model = User
        fields = cross_app_serializers.UserSerializer.Meta.fields + [
            'active_subscription'
        ]