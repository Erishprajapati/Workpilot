# project/serializers.py
from rest_framework import serializers
from .models import Project, ProjectDocuments, Tasks
from employee.serializers import *
from employee.models import Employee
# from employee.models import Employee

# class EmployeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employee
#         fields = ['id', 'user', 'role', 'employee_code']

class ProjectDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocuments
        fields = ['id', 'file', 'description', 'uploaded_at']

class ProjectSerializer(serializers.ModelSerializer):
    manager = EmployeeNestedMinimalSerializer(read_only=True)
    team_lead = EmployeeNestedMinimalSerializer(read_only=True)
    members = EmployeeNestedMinimalSerializer(read_only=True, many=True)
    documents = ProjectDocumentSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'department',
            'manager', 'team_lead', 'members', 'documents',
            'start_date', 'end_date', 'is_active'
        ]

class ProjectMemberUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), many=True)

    class Meta:
        model = Project
        fields = ['members']

class ProjectDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocuments
        fields = ['project', 'file', 'description']
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeNestedMinimalSerializer(read_only=True)
    created_by = EmployeeNestedMinimalSerializer(read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    class Meta:
        model = Tasks
        fields = "__all__"
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'start_date', 'is_active', 'reviewed_by']

    def validate(self, data):
        project = data.get("project")
        title = data.get("title") 

        if project and title and Tasks.objects.filter(project=project, title__iexact=title).exists():
            raise serializers.ValidationError(
                {"title": "A task with this title already exists in this project."}
            )
        return data

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     employee = getattr(user, 'employee_profile', None)
    #     if not employee:
    #         raise serializers.ValidationError({"detail": "User has no associated employee profile."})

    #     project = validated_data.pop('project')

    #     task = Tasks.objects.create(
    #         project=project,
    #         created_by=employee,
    #         **validated_data
    #     )
    #     return task

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProjectEmployeeNestedSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Only show name and email

    class Meta:
        model = Employee
        fields = ['id', 'user']

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email
        }