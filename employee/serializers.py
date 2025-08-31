from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers, status
from .models import *
from rest_framework.response import Response


user = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    class Meta:
        fields = ['username','password', 'email', 'first_name', 'last_name']
        model = User

        def create(self, validated_data):
            return User.objects.create_user(**validated_data)   
        
class EmployeeStatusSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required = False, default = False)
    class Meta:
        model = EmployeeStatus
        fields = "__all__"

class EmployeeNestedMinimalSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'user']

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email
        }

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]

    def create(self, validated_data):
        # use email as username
        return User.objects.create_user(
            username=validated_data["email"],   # email as username
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
    
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {
            "dob": {"required": True},
            "gender": {"required": True},
            "current_address": {"required": True},
            "permanent_address": {"required": True},
            "phone": {"required": True},
        }

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer().create(user_data)  # call nested serializer
        employee = Employee.objects.create(user=user, **validated_data)
        return employee

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance: Employee, validated_data: dict) -> Employee:
        # Handle nested user update
        user_data = validated_data.pop("user", None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Update Employee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance  # Return instance, not Response
class DepartmentSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required = False, default = False)
    class Meta:
        model = Department
        fields = "__all__"
        
        def create(self, validated_data:dict)->Department:
            hr = validated_data.pop("hr", None)
            department = Department.objects.create(**validated_data)
            if hr:
                department.hr = hr
                department.save()
            return department
        
        def update(self, instance, validated_data:dict):
            instance.name = validated_data.get("name", instance.name)
            if "hr" in validated_data:
                instance.hr = validated_data.get("hr")
            instance.save()
            return instance

class DepartmentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["name", "description"]

    
class EmployeeProfileSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = EmployeeProfile
        fields = [
            "employee",
            "profile_photo",
            "citizenship",
            "contact_agreement",
        ]