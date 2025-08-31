from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from .models import * 
from .serializers import *
from employee.models import * 
from rest_framework import viewsets, permissions
from employee.permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, ProjectDocuments
from .serializers import *
from employee.models import Employee
from .permissions import *  
from django.db.models import Min
from employee.permissions import *

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.annotate(
        earliest_deadline = Min('end_date')
    )
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsHRorSuperUser, IsProjectManagerOrSuperUserOrHR]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'priority']
    ordering = ['name']

    def get_queryset(self):
        """
        Filter projects based on employee role:
        - HR/Admin: all projects
        - Project Manager: projects they manage
        - Team Lead: projects they lead
        - Employee: projects they are assigned to
        """
        employee = getattr(self.request.user, "employee_profile", None)
        if not employee:
            return Project.objects.none()

        role = employee.role
        if role in [Employee.HR, Employee.ADMIN]:
            return Project.objects.all()
        elif role == Employee.PROJECT_MANAGER:
            return Project.objects.filter(manager=employee)
        elif role == Employee.TEAM_LEAD:
            return Project.objects.filter(team_lead=employee)
        elif role == Employee.EMPLOYEE:
            return Project.objects.filter(members=employee)
        return Project.objects.none()

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user as the creator.
        If the creator is a project manager, they are also assigned as the manager.
        """
        employee = getattr(self.request.user, "employee_profile", None)
        if not employee:
            return Response({"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST)

        role = getattr(employee, "role", None)
        if role == Employee.PROJECT_MANAGER:
            serializer.save(created_by=employee, manager=employee)
        else:
            serializer.save(created_by=employee)

    @action(detail=True, methods=['post'])
    def assign_members(self, request, pk=None):
        """
        Assign or update project members.
        """
        project = self.get_object()
        serializer = ProjectMemberUpdateSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Members updated successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def assign_manager(self, request, pk=None):
        """
        Assign a project manager (for HR/Admin only).
        """
        employee = getattr(request.user, "employee_profile", None)
        if not employee or employee.role not in [Employee.HR, Employee.ADMIN]:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        project = self.get_object()
        manager_id = request.data.get("manager_id")
        if not manager_id:
            return Response({"error": "manager_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manager = Employee.objects.get(id=manager_id, role=Employee.PROJECT_MANAGER)
        except Employee.DoesNotExist:
            return Response({"error": "Invalid manager"}, status=status.HTTP_400_BAD_REQUEST)

        project.manager = manager
        project.save()
        return Response({"message": "Manager assigned successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """
        Upload documents to a project.
        """
        project = self.get_object()
        serializer = ProjectDocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)  # Associate the document with the project
        return Response({"message": "Document uploaded successfully"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        List all documents of the project.
        """
        project = self.get_object()
        documents = ProjectDocuments.objects.filter(project=project)
        serializer = ProjectDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssignedEmployeeOrReviewer, IsProjectManagerOrSuperUserOrHR ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'assigned_to__user__first_name', 'assigned_to__user__last_name']
    ordering_fields = ['title', 'status', 'priority', 'due_date']
    ordering = ['title']
    filterset_fields = ['status', 'priority', 'assigned_to', 'project']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Tasks.objects.none()

        employee = getattr(user, "employee_profile", None)
        if not employee:
            return Tasks.objects.none()
        # Base queryset
        queryset = Tasks.objects.all()

        # Apply nested filter if project_pk exists
        project_id = self.kwargs.get('project_pk')  # Provided by nested router
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # RBAC: HR / ADMIN / PM / TEAM_LEAD -> all tasks
        if employee.role in [Employee.HR, Employee.ADMIN, Employee.PROJECT_MANAGER, Employee.TEAM_LEAD]:
            return queryset

        # Regular employee -> only their tasks
        return queryset.filter(assigned_to=employee)
    def perform_create(self, serializer):
        employee = getattr(self.request.user, "employee_profile", None)
        project = Project.objects.get(pk=self.kwargs.get("project_pk"))
        serializer.save(created_by=employee, project=project)


    def perform_update(self, serializer):
        """Handle task review workflow"""
        task = serializer.instance
        status_value = self.request.data.get("status")

        employee = getattr(self.request.user, "employee_profile", None)

        # Assigned employee submits for review
        if status_value == "review" and employee == task.assigned_to:
            task.status = "review"

        # PM / TL / HR / Admin approves and marks as completed
        elif status_value == "completed" and employee and employee.role in ["PROJECT_MANAGER", "TEAM_LEAD", "HR", "ADMIN"]:
            task.status = "completed"
            task.reviewed_by = employee

        task.save()
        serializer.save()

class IsProjectAuthorized(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:   
            return False

        employee = getattr(request.user, "employee_profile", None)
        if not employee:
            return False

        if view.action == "create":
            return employee.role in [Employee.HR, Employee.ADMIN, Employee.PROJECT_MANAGER]

        return True