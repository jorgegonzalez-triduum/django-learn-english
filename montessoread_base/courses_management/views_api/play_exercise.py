from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import PlayExercise, PlayExerciseStatus, PlayExerciseTry
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.views import APIView, status
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.views_api.base import BaseVs
from courses_management import globals as choices

class PlayExerciseViewSet(
                        BaseVs,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):

    queryset = PlayExercise.objects.select_related(
        'exercise').prefetch_related(
            'playexercisetry_set', 'playexercisetry_set__playexercisestatus_set').all()
    search_fields = ['exercise__name']
    serializer_class = serializers.PlayExerciseSerializer
    parser_classes = (MultiPartParser, JSONParser)
    
    def retrieve(self, request, pk=None):
        instance = self.get_object()
        if request.GET.get('restart') == 'true':
            new_try = PlayExerciseTry(
                play_exercise=instance,
                try_number=instance.playexercisetry_set.all().last().try_number + 1)
            new_try.save()
            instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(self.serializer_class(
            instance=instance,
            context={'request':request}
            ).data)
    
    
    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        instance = self.get_object()
        data = request.data.copy()
        data['play_exercise_try'] = serializers.PlayExerciseTrySerializer(
            instance=instance.playexercisetry_set.all().last(),
            context={'request':request}).data['url']
        serializer = serializers.PlayExerciseStatusSerializer(data=data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        return Response(self.serializer_class(
            instance=instance,
            context={'request':request}
            ).data)

    @action(detail=True, methods=['put'])
    def update_results(self, request, pk=None):
        instance = self.get_object()
        data = request.data.copy()
        data['play_exercise_try'] = serializers.PlayExerciseTrySerializer(
            instance=instance.playexercisetry_set.all().last(),
            context={'request':request}).data['url']
        serializer = serializers.PlayExerciseResultSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        return Response(self.serializer_class(
            instance=instance,
            context={'request':request}
            ).data)