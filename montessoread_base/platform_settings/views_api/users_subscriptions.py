from rest_framework.parsers import JSONParser, MultiPartParser
from platform_settings.models import UserSubscription, StudentSubscription, SubscriptionExercise
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from platform_settings import serializers
from rest_framework.response import Response
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, status
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.views_api.base import BaseVs
import django_filters


class UserSubscriptionFilter(django_filters.FilterSet):
    class Meta:
        model = UserSubscription
        fields = {
            'user': ['exact']
        }

class SubscriptionExerciseFilter(django_filters.FilterSet):
    class Meta:
        model = SubscriptionExercise
        fields = {
            'subscription__id': ['exact', 'in']
        }

class UserSubscriptionViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # permission_classes = []
    
    permissions_required = ('auth.section_perm_user_subscriptions',)
    
    permission_classes_custom = [DjangoPermissions, IsAuthenticated]
    
    permission_classes_by_action = {
        'create': permission_classes_custom,
        'list': permission_classes_custom,
        'retrieve': permission_classes_custom,
        'update': permission_classes_custom,
        'destroy': permission_classes_custom,
        'alls': permission_classes_custom,
    }

    queryset = UserSubscription.objects.all()
    search_fields = [
        'name',
        'user__username',
        'subscription__name', 'user__first_name', 'user__last_name', 'user__email',
        'start_date', 'end_date']
    serializer_class = serializers.UserSubscriptionSerializer
    filterset_class = UserSubscriptionFilter
    ordering = ['name', 'user__first_name', 'user__last_name', 'user__email', 'start_date', 'end_date']
    
    @action(detail=False, methods=['get'])
    def alls(self, request, pk=None):
        serializer_class = self.serializer_class
        queryset = self.filter_queryset(UserSubscription.alls.all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(
                page, many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = serializer_class(
            queryset, many=True,
            context={'request': request})
        return Response(serializer.data)
    
class StudentSubscription(BaseModelViewSet):

    queryset = StudentSubscription.objects.all()
    serializer_class = serializers.StudentSubscriptionSerializer

class SubscriptionExerciseView(
                        BaseVs,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    queryset = SubscriptionExercise.objects.all()
    serializer_class = serializers.SubscriptionExerciseSerializer
    permissions_required = ('')
    search_fields = [
        'exercise__name'
    ]
    filterset_class = SubscriptionExerciseFilter


