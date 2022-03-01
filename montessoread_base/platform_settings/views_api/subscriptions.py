from rest_framework.parsers import JSONParser, MultiPartParser
from platform_settings.models import Subscription
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from platform_settings import serializers
from rest_framework.response import Response
from rest_framework.views import APIView, status

class SubscriptionViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # permission_classes = []
    queryset = Subscription.objects.all()
    search_fields = [
        'name',
        'students_number',
        'days_term']
    serializer_class = serializers.SubscriptionSerializer
    
    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = serializers.SubscriptionDetailSerializer(
            instance=instance,
            context={'request': request})
        return Response(serializer.data)