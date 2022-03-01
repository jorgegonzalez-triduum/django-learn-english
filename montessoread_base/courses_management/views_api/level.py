from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import Level
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.views import APIView, status
from triduum_resource.cross_app.views_api.base import BaseVs
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from courses_management.permissions import HasSubscriptionOrIsAdmin
from rest_framework.permissions import IsAuthenticated

class LevelViewSet(BaseModelViewSet):

    permissions_required = ('auth.section_perm_levels',)
    queryset = Level.objects.all()
    search_fields = ['level__name', 
                    'name', 
                    'video_url']
                    
    serializer_class = serializers.LevelSerializer
    parser_classes = (MultiPartParser, JSONParser)

    permission_classes_custom = [DjangoPermissions, IsAuthenticated]
    
    permission_classes_by_action = {
        'create': permission_classes_custom,
        'list': permission_classes_custom,
        'retrieve': permission_classes_custom,
        'update': permission_classes_custom,
        'destroy': permission_classes_custom,
        'set_image': permission_classes_custom,
        'get_ext_exercises': [IsAuthenticated, HasSubscriptionOrIsAdmin],
    }

    @action(detail=True, methods=['put'])
    def set_image(self, request, pk=None):
        image = self.get_object()
        serializer = serializers.LevelImageSerializer
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

    @action(detail=True, methods=['get'])
    def get_ext_exercises(self, request, pk=None):
        instance = self.get_object()
        queryset = instance.exercise_set
        if self.user_subscription_instance and not request.user.is_superuser:
            queryset = queryset.filter(
                id__in = self.user_subscription_instance.subscription.exercises.all(
                    ).values_list('id', flat=True))
        else:
            queryset = queryset.all()
        serializer = serializers.ExerciseSerializer(
            queryset.order_by('order'), many=True,
            context={'request':request})
        return Response(serializer.data)