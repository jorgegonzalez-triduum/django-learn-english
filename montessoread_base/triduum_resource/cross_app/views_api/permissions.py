from django.contrib.auth.models import Permission
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from triduum_resource.cross_app import serializers


class PermissionViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAdmin]
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    search_fields = ['id', 'name', 'codename',
                    'content_type__app_label', 'content_type__model']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer_fields = ['url', 'id', 'name', 'codename',
            'content_type', 'user_set', 'group_set']
        if page is not None:
            serializer = self.serializer_class(
                page, many=True,
                fields=serializer_fields,
                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(
            queryset, many=True,
            fields=serializer_fields,
            context={'request': request})
        return Response(serializer.data)