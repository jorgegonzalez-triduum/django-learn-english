from triduum_resource.cross_app.models import CompanyInformation
from triduum_resource.cross_app.rest_framework.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app.views_api.base import BaseVs
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView, status
from triduum_resource.cross_app import serializers
from rest_framework.response import Response


class CompanyInformationViewSet(BaseVs,
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAdmin]
    queryset = CompanyInformation.objects.all()
    serializer_class = serializers.CompanyInformationSerializer
    search_fields = ['id', 
                    'company_name', 
                    'phone_number', 
                    'whatsapp_number', 
                    'contact_email', 
                    'support_email', 
                    'instagram_name', 
                    'instagram_url', 
                    'facebook_name', 
                    'facebook_url', 
                    ]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list','retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]


    @action(detail=True, methods=['put'])
    def set_file(self, request, pk=None):
        c_i = self.get_object() #Company info object
        serializer = serializers.CompanyInformationFilesSerializer
        allowed_fields = ('light_logo', 'dark_logo', 'short_light_logo', 'short_dark_logo')
        keys_to_update = []
        for key in request.data.keys():
            if not key in allowed_fields:
                return Response({'detail': 'Not allowed field'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                keys_to_update.append(key)
        c_i_file_srlzr = serializer(
                        instance=c_i,
                        fields=keys_to_update,
                        data=request.data,
                        context={'request':request}
                        )
        if c_i_file_srlzr.is_valid():
            c_i_file_srlzr.save()
            return Response(self.serializer_class(
                instance=c_i_file_srlzr.instance,
                context={'request':request}
                ).data)
        else:
            return Response(c_i_file_srlzr.errors,
                            status=status.HTTP_400_BAD_REQUEST)