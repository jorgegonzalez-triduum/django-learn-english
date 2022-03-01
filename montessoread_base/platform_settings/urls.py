from django.urls import path, include
from rest_framework import routers
from platform_settings.views_api import subscriptions, users_subscriptions

router = routers.DefaultRouter()
router.register(r'subscriptions', subscriptions.SubscriptionViewSet)
router.register(r'users_subscriptions', users_subscriptions.UserSubscriptionViewSet)
router.register(r'student_subscription', users_subscriptions.StudentSubscription)
router.register(r'subscription_exercise', users_subscriptions.SubscriptionExerciseView)

urlpatterns = [
    path('', include(router.urls)),
]