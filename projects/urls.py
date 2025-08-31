# project/urls.py
from rest_framework_nested import routers
from django.urls import path, include
from .views import ProjectViewSet, TaskViewSet

# Base router for projects
router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

# Nested router for tasks under projects
projects_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'tasks', TaskViewSet, basename='project-tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
]