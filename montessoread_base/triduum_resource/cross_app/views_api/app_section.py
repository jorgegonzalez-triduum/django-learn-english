from django.contrib.auth.models import Permission
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from triduum_resource.cross_app.models import AppSection
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from triduum_resource.cross_app import serializers
import django_filters

class AppSedctionFilter(django_filters.FilterSet):
    class Meta:
        model = AppSection
        fields = {
            'admin_required': ['exact'],
            'app_permission': ['isnull'],
        }
        
        
class AppSection(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAdmin]
    queryset = AppSection.objects.all()
    serializer_class = serializers.AppSectionSerializer
    search_fields = ['name', 'path', 'hover_text', 'icon_name','admin_required']
    filterset_class = AppSedctionFilter