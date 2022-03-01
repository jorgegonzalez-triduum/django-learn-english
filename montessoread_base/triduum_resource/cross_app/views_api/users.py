from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework import filters
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app import serializers
from triduum_resource.cross_app.views_api.base import BaseModelViewSet, BaseVs
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.models import UserInfo
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.translation import gettext as _

class UserViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.prefetch_related(
        'user_permissions', 'groups').all()
    serializer_class = serializers.UserSerializer
    search_fields = ['username', 'email', 'first_name', 'last_name']
    permission_classes = [IsAdmin]
    parser_classes = (MultiPartParser, JSONParser)
    filterset_fields = ['username', 'groups']

    @action(detail=True, methods=['put'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = serializers.PasswordSerializer(
            instance=user, data=request.data,
            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'status': _('Password set successfully')})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def for_options(self, request, pk=None):
        serializer_class = serializers.UserGroupSerializer
        queryset = self.filter_queryset(self.get_queryset())
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

    @action(detail=True, methods=['put'])
    def set_photo(self, request, pk=None):
        user = self.get_object()
        user_srlizer_url = serializers.UserSerializer(
                        instance=user,
                        context={'request':request}
                        ).data['url']
        data = request.data
        if data:
            data['user'] = user_srlizer_url
        try:
            user_info = UserInfo.objects.get(user=user)
        except ObjectDoesNotExist:
            user_info = None
        if not user_info:
            u_i_srlz = serializers.UserInfoSerializer(
                data=data,
                context={'request': request})
        else:
            u_i_srlz = serializers.UserInfoSerializer(
                instance=user_info, data=data,
                context={'request': request})
        if u_i_srlz.is_valid():
            u_i_srlz.save()
            return Response(serializers.UserSerializer(
                        instance=u_i_srlz.instance.user,
                        context={'request':request}
                        ).data)
        else:
            return Response(u_i_srlz.errors,
                            status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer_fields = [
            'url', 'id', 'username', 'first_name', 'last_name',
            'email', 'is_staff', 'is_superuser','is_active',
            'user_info', 'groups', 'user_permissions',
            'user_permissions_filtered', 'app_sections_users', 'subscription_active']
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

class UserInfoViewSet(BaseVs,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):

    queryset = UserInfo.objects.all()
    serializer_class = serializers.UserInfoSerializer
    search_fields = ['user__username', 'photo']
    permission_classes = [IsAdmin]