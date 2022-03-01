from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import PlayExerciseResult
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from rest_framework.decorators import action
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.views import APIView, status
from rest_framework import viewsets, mixins
from triduum_resource.cross_app.views_api.base import BaseVs

class PlayExerciseResultViewSet(
                        BaseVs,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):

    queryset = PlayExerciseResult.objects.all()
    search_fields = ['']
    serializer_class = serializers.PlayExerciseResultSerializer
    parser_classes = (MultiPartParser, JSONParser)