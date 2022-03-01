from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.views import status
from django.utils.translation import gettext as _
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from triduum_resource.cross_app.views_api.base import BaseVs, BaseModelViewSet
from triduum_resource.cross_app import serializers
from triduum_resource.cross_app.models import GroupInfo


class GroupViewSet(BaseModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = [IsAdmin]
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    search_fields = ['name', 'group_info__description']


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer_fields = [
            'url', 'id', 'name', 'permissions',
            'user_set', 'group_info']
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

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        if group.user_set.all().exists():
            return Response({
                'detail': _('The group you want to delete still has users assigned')
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class GroupInfoViewSet(BaseVs,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):

    queryset = GroupInfo.objects.all()
    serializer_class = serializers.GroupInfoSerializer
    search_fields = ['group__name', 'description']
    permission_classes = [IsAdmin]