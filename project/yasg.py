from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Comment-service API",
        default_version="v1",
        description="Base comments service",
        license=openapi.License(name="My License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('readoc/', schema_view.with_ui('redoc', cache_timeout=0))

]
