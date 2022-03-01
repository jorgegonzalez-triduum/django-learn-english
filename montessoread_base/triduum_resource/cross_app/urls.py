from django.urls import path, include
from rest_framework import routers
from .views_api import (
    users, groups, permissions, app_permissions, 
    app_section, content_type,
    company_information)

router = routers.DefaultRouter()
router.register(r'users', users.UserViewSet)
router.register(r'groups', groups.GroupViewSet)
router.register(r'groups-info', groups.GroupInfoViewSet)
router.register(r'perms', permissions.PermissionViewSet)
router.register(r'content-type', content_type.ContentTypeViewSet)
router.register(r'app-perms', app_permissions.AppPermissionViewSet)
router.register(r'app-sections', app_section.AppSection)
router.register(r'users-info', users.UserInfoViewSet)
router.register(r'company-info', company_information.CompanyInformationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]