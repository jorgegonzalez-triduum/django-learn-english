from django.contrib.contenttypes.models import ContentType
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from triduum_resource.cross_app.views_api.base import BaseVs
from rest_framework import viewsets, mixins
from triduum_resource.cross_app import serializers


class ContentTypeViewSet(BaseVs,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAdmin]
    queryset = ContentType.objects.all()
    serializer_class = serializers.ContentTypeSerializer
    search_fields = ['id', 'app_label', 'model']