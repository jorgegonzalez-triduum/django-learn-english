from rest_framework.parsers import JSONParser, MultiPartParser
from courses_management.models import QualificationTeacherExercise
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from courses_management import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from triduum_resource.cross_app.rest_framework.permissions import DjangoPermissions
from rest_framework.views import APIView, status


class QualificationTeacherVs(BaseModelViewSet):

    queryset = QualificationTeacherExercise.objects.all()
    search_fields = ['']
    serializer_class = serializers.QualificationTeacherSerializer