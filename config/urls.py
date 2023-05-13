from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

sxema = get_schema_view(
    openapi.Info(
        title="Blog Api",
        description="Oddiy loyiha",
        default_version="1.0.0",
        terms_of_service="https://www.google.com/policies/terms",
        contact=openapi.Contact(email='freejobmakery@gmail.com'),
        license=openapi.License(name="Project litsenziyasi")),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/', include('api.urls')),
                  path("swagger/", sxema.with_ui('swagger', cache_timeout=0), name="swagger"),
                  path("redoc/", sxema.with_ui('redoc', cache_timeout=0), name="redoc"),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
