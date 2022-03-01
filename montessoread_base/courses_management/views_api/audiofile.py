from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import AudioFile
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.views import APIView, status
from courses_management.lib import speech_to_text

class AudioFileViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # permission_classes = []
    queryset = AudioFile.objects.all()
    search_fields = ['model', 
                    'related_id', 
                    'file']
                    
    serializer_class = serializers.AudioFileSerializer
    parser_classes = (MultiPartParser, JSONParser)

    
    @action(detail=True, methods=['put'])
    def set_order(self, request, pk=None):
        audio = self.get_object()
        audio_file_order_srlzr = self.serializer_class(
                        instance=audio,
                        fields=['order'],
                        data=request.data,
                        context={'request':request}
                        )
        if audio_file_order_srlzr.is_valid():
            audio_file_order_srlzr.save()
            return Response(self.serializer_class(
                instance=audio_file_order_srlzr.instance,
                context={'request':request}
                ).data)
        else:
            return Response(audio_file_order_srlzr.errors,
                            status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['post'])    
    def speech_to_text(self, request):
        results = []
        audio_file = request.data.get('audio-file')
        if not isinstance(audio_file, str):
            results = speech_to_text.sample_recognize(content=audio_file.read())
            if results:
                results = [ x.alternatives[0].transcript for x in results ]
        return Response({'results': results})
