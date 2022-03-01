from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', include('triduum_resource.cross_app.urls')),
    path('api-auth/', include('triduum_resource.cross_app.urls_auth')),

    path('courses_management/', include('courses_management.urls')),
    path('platform_settings/', include('platform_settings.urls')),
    path('classroom/', include('classroom.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)