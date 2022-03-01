from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import PlayExerciseTry
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.views import APIView, status
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.views_api.base import BaseVs

class PlayExerciseTryViewSet(
                        BaseVs,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    queryset = PlayExerciseTry.objects.select_related(
        'play_exercise').all()
    search_fields = ['play_exercise__exercise_name']
    serializer_class = serializers.PlayExerciseTrySerializer
    parser_classes = (MultiPartParser, JSONParser)