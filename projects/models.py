from django.db import models
from employee.models import *
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Project(Timestamp):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    """
    limiting to project manager only gives access to project managers
    """
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank= True, null = True)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name="managed_projects")
    team_lead = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name="lead_projects")
    members = models.ManyToManyField(Employee, related_name="assigned_to", blank = True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name="created_projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    
class ProjectDocuments(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null = True, related_name = "documents")
    file = models.FileField(upload_to="project/documents")
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project.name

class Tasks(models.Model):
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("review", "In Review")
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent")
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    start_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="created_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_tasks")
    def __str__(self):
        return self.title