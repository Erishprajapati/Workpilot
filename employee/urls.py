from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "employee"

router = DefaultRouter()
router.register(r'employee-status', EmployeeStatusViewSet)
router.register(r'employee', EmployeeViewSet)
router.register(r'employee-profile', EmployeeProfileViewSet)
router.register(r'department', DepartmentViewSet)
urlpatterns = [
    path('', include(router.urls))
]