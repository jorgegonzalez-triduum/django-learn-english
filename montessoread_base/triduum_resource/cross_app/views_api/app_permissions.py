from rest_framework.response import Response
from rest_framework.views import status
from triduum_resource.cross_app.models import AppPermission
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from triduum_resource.cross_app import serializers
from django.utils.translation import gettext as _


class AppPermissionViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAdmin]
    queryset = AppPermission.objects.all()
    serializer_class = serializers.AppPermissionSerializer
    search_fields = ['id', 'permission__name', 'permission__codename', 'permission_type']
    filterset_fields = ['permission_type']

    def destroy(self, request, *args, **kwargs):
        app_permission = self.get_object()
        if app_permission.permission.user_set.all().exists():
            return Response({
                'detail': _('The permission you want to delete still has users assigned')
            }, status=status.HTTP_400_BAD_REQUEST)
        if app_permission.permission.group_set.all().exists():
            return Response({
                'detail': _('The permission you want to delete still has groups assigned')
            }, status=status.HTTP_400_BAD_REQUEST)
        perm = app_permission.permission
        perm.codename = '{}-deleted'.format(
            perm.codename
        )
        perm.save()
        return super().destroy(request, *args, **kwargs)
    
    def retrieve(self, request, pk=None):
        app_permission = self.get_object()
        serializer = serializers.AppPermissionDetailSerializer(
            instance=app_permission,
            context={'request': request})
        return Response(serializer.data)