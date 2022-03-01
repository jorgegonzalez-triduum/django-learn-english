from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import viewsets
from rest_framework import filters
from triduum_resource.cross_app.rest_framework.filters import RelatedOrderingFilter
from triduum_resource.cross_app import serializers
from django_filters.rest_framework import DjangoFilterBackend

class BaseVs():
    '''
    Base view for DRF ViewSets
    '''
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, RelatedOrderingFilter]
    search_fields = []
    ordering = ['id']
    permissions_required = []
    # permission_classes = []
    
    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     return [permission() for permission in self.permission_classes]
    
    # Refer to https://stackoverflow.com/a/35987077/1677041
    # permission_classes_by_action = {
    #     'create': permission_classes,
    #     'list': permission_classes,
    #     'retrieve': permission_classes,
    #     'update': permission_classes,
    #     'destroy': permission_classes,
    # }
    
    permission_classes_by_action = {}
    
    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            if self.action:
                action_func = getattr(self, self.action, {})
                action_func_kwargs = getattr(action_func, 'kwargs', {})
                permission_classes = action_func_kwargs.get('permission_classes')
            else:
                permission_classes = None

            return [permission() for permission in (permission_classes or self.permission_classes)]




    def perform_destroy(self, instance):
        if not hasattr(instance, 'disable'):
            instance.delete()
        else:
            instance.disable()
    
class BaseViewSet(BaseVs, viewsets.ViewSet):
    pass

class BaseModelViewSet(BaseVs, viewsets.ModelViewSet):
    pass