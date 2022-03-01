from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management import models
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.views import APIView, status
from triduum_resource.cross_app.views_api.base import BaseVs
from rest_framework import viewsets, mixins

class SectionViewSet(BaseModelViewSet):

    permissions_required = ('auth.section_perm_sections',)
    queryset = models.Section.objects.all()
    search_fields = ['level__name', 
                    'name', 
                    'video_url']
                    
    serializer_class = serializers.SectionSerializer
    parser_classes = (MultiPartParser, JSONParser)

    @action(detail=True, methods=['put'])
    def set_image(self, request, pk=None):
        image = self.get_object()
        serializer = serializers.SectionImageSerializer
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

    @action(detail=False, methods=['get'])
    def get_ext_sections(self, request):
        if self.request.user.is_superuser:
            qs = models.Section.objects.all().order_by('order')
        else:
            qs = models.Section.objects.all().order_by('order')
        queryset = qs
        sections_allowed_ids = []
        for section in queryset:
            for lv in section.level_set.all():
                if lv.exercise_set.all().count():
                    sections_allowed_ids.append(section.id)
                    break
        queryset = queryset.filter(id__in=sections_allowed_ids).order_by('order')
        serializer = self.serializer_class(queryset, many=True,
            context={'request':request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def get_ext_levels(self, request, pk=None):
        instance = self.get_object()
        serializer = serializers.LevelSerializer(
            instance.level_set.all().order_by('order'), many=True,
            context={'request':request})
        return Response(serializer.data)