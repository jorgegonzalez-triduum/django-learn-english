from courses_management.models import Alphabet
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from courses_management import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView, status



class AlphabetViewSet(BaseModelViewSet):
    # permission_classes = []
    
    permissions_required = ('auth.section_perm_alphabet',)
    queryset = Alphabet.objects.all()
    serializer_class = serializers.AlphabetSerializer
    search_fields = ['order',
                    'letter',
                    'pronunciation',
                    'image',]
    
    ordering = ['order']

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