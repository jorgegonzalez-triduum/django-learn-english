from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import Category
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.views import APIView, status

class CategoryViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    permissions_required = ('auth.section_perm_categories',)
    queryset = Category.objects.all()
    remove_fields = ['parent']
    search_fields = ['name', 
                    'parent__name', 
                    'icon_name', 
                    'color', 
                    'image', 
                    'order', 
                    'hover_text']
                    
    serializer_class = serializers.CategorySerializer
    parser_classes = (MultiPartParser, JSONParser)



    @action(detail=True, methods=['put'])
    def set_image(self, request, pk=None):
        image = self.get_object() #Company info object
        serializer = serializers.CategoryImageSerializer
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