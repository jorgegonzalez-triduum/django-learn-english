from django.utils.translation import gettext as _
from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import Object
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from courses_management.models import Exercise
from rest_framework.response import Response
from rest_framework.views import APIView, status

class ObjectViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permissions_required = ('auth.section_perm_objects',)
    queryset = Object.objects.all()
    remove_fields = ['category']
    search_fields = ['category__name', 
                    'category__parent__name',
                    'name', 
                    'description', 
                    'icon_name', 
                    'image']
                    
    serializer_class = serializers.ObjectSerializer
    parser_classes = (MultiPartParser, JSONParser)
    

    
    @action(detail=True, methods=['put'])
    def set_image(self, request, pk=None):
        image = self.get_object() #Company info object
        serializer = serializers.ObjectImageSerializer
        image_file_srlzr = serializer(
                        instance=image,
                        fields=['image'],
                        data=request.data,
                        context={'request':request}
                        )
        if image_file_srlzr.is_valid():
            image_file_srlzr.save()
            return Response(self.serializer_class(
                instance=image_file_srlzr.instance,
                context={'request':request}
                ).data)
        else:
            return Response(image_file_srlzr.errors,
                            status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['put'])
    def set_audio(self, request, pk):
        serializer = serializers.AudioFileSerializer
        audio_file_srlzr = serializer(
                        data=request.data,
                        context={'request':request}
                        )

        if audio_file_srlzr.is_valid():
            audio_file_srlzr.save()
            object_instance = self.get_object() #Object object
            return Response(self.serializer_class(
                instance=object_instance,
                context={'request':request}
                ).data)
        else:
            return Response(audio_file_srlzr.errors,
                            status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        object_ = self.get_object()
        exercises = Exercise.objects.all()
        ocurrences = 0
        for exercise in exercises:
            if str(object_.id) in str(exercise.definition.get('materials')).replace(',','').replace('[','').replace(']','').replace(' ',',').split(','):
                ocurrences += 1

        if ocurrences > 0:
            return Response({
                'detail': _('Error: The object you want to delete is assigned to at least {} exercise(s)'.format(ocurrences))
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)