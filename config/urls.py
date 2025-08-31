from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# from projects.views import GoogleLogin

schema_view = get_schema_view(
    openapi.Info(
        title="Project Management API",
        default_version="v1",
        description="API documentation for Project Management",
        contact=openapi.Contact(email="irish@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # 👇 keep all APIs under /api/
    path("api/employees/", include("employee.urls", namespace="employee")),
    path("api/projects/", include("projects.urls")),
    path("api/auth/", include("authentication.urls", namespace="authentication")),

    # Optional third-party auth (only keep if using allauth / dj-rest-auth)
    # path("api/auth/google/", GoogleLogin.as_view(), name="google-login"),
    path("accounts/", include("allauth.urls")),

    # Browsable API login/logout
    path("api-auth/", include("rest_framework.urls")),

    # API Docs
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)