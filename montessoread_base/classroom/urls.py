from django.urls import path, include
from rest_framework import routers
from .views_api import student

router = routers.DefaultRouter()
router.register(r'student', student.StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]