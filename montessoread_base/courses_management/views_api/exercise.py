from django.core.cache import cache
from courses_management import serializers
from courses_management.models import Exercise, Section
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.views import APIView, status
from courses_management.permissions import HasSubscriptionOrIsAdmin

cache_timeout_cnx = 3000


class ExerciseViewSet(BaseModelViewSet):

    permission_classes_custom = [DjangoPermissions, IsAuthenticated]
    permissions_required = ('auth.section_perm_exercises',)
    queryset = Exercise.objects.select_related('level', 'level__section').all()
    search_fields = ['level__name', 
                    'name', 
                    'video_url']
    ordering = ['level__section__order', 'level__order', 'order']
    serializer_class = serializers.ExerciseSerializer
    parser_classes = (MultiPartParser, JSONParser)
    
    permission_classes_by_action = {
        'create': permission_classes_custom,
        'list': permission_classes_custom,
        'retrieve': permission_classes_custom,
        'update': permission_classes_custom,
        'destroy': permission_classes_custom,
        'set_image': permission_classes_custom,
        'set_definition': permission_classes_custom,
        'get_ext_exercises': [IsAuthenticated, HasSubscriptionOrIsAdmin],
        'get_ext_exercise_detail': [IsAuthenticated, HasSubscriptionOrIsAdmin],
        'get_ext_exercises_by_sections': [IsAuthenticated, HasSubscriptionOrIsAdmin],
        'play_exercise': [IsAuthenticated, HasSubscriptionOrIsAdmin],
    }

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
    def get_ext_exercises(self, request, pk=None):
        serializer = serializers.ExerciseSerializer(
            self.get_queryset().order_by('level__section__order', 'level__order', 'order'), many=True,
            context={'request':request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_ext_exercises_by_sections(self, request, pk=None):
        user = request.user
        if cache.get(f"{user.username}_get_ext_exercises_by_sections"):
            final_data_sections = cache.get(f"{user.username}_get_ext_exercises_by_sections")
        else:
            allowed_exercises = Exercise.objects
            allowed_sections = Section.objects
            if self.user_subscription_instance and not user.is_superuser:
                allowed_exercises = allowed_exercises.filter(
                    id__in = self.user_subscription_instance.subscription.subscriptionexercise_set.all(
                        ).values_list('exercise__id', flat=True))
                allowed_sections = allowed_sections.filter(
                    id__in=allowed_exercises.values_list('level__section', flat=True)
                )
            else:
                allowed_exercises = allowed_exercises.all()
                allowed_sections = allowed_sections.all()
            sections = serializers.SectionSerializer(
                allowed_sections.order_by('order'), many=True,
                context={'request':request}
                ).data
            
            final_data_sections = []
            for section in sections:
                if section['exercises_count']:
                    section['exercises'] = serializers.ExerciseSerializerLite(
                        allowed_exercises.filter(level__section__id = section['id']).order_by(
                            'level__section__order', 'level__order', 'order'), many=True,
                            context={'request':request}).data
                    final_data_sections.append(section)        
            cache.set("get_ext_exercises_by_sections", final_data_sections, cache_timeout_cnx)
        return Response(final_data_sections)
    
    @action(detail=True, methods=['get'])
    def get_ext_exercise_detail(self, request, pk=None):
        exercise = self.get_object()
        if cache.get("get_ext_exercise_detail_{}".format(exercise.id)):
            serializer_ = cache.get("get_ext_exercise_detail_{}".format(exercise.id))
        else:
            serializer_ = serializers.ExerciseSerializer(
                exercise,
                context={'request':request}
                ).data
            cache.set("get_ext_exercise_detail_{}".format(exercise.id), serializer_, cache_timeout_cnx)
        return Response(serializer_)

    @action(detail=True, methods=['put'])
    def play_exercise(self, request, pk=None):
        exercise = self.get_object()
        exercise_url = self.serializer_class(
            instance=exercise,
            context={'request':request}
        ).data['url']
        serializer = serializers.PlayExerciseSerializer(
            data={
                'exercise': exercise_url,
                'student': request.data.get('student_url')},
            context={'request':request}
            )
        if serializer.is_valid():
            instance_play = serializer.save()
            return Response(instance_play)
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def set_definition(self, request, pk=None):
        exercise = self.get_object()
        serializer = serializers.ExerciseDefinitionSerializer
        exercise_serializer = serializer(
                        instance=exercise,
                        data=request.data,
                        context={'request':request}
                        )
        if exercise_serializer.is_valid():
            exercise_serializer.save()
            return Response(self.serializer_class(
                instance=exercise_serializer.instance,
                context={'request':request}
                ).data)
        else:
            return Response(exercise_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
