from rest_framework import serializers
from django.contrib.auth import get_user_model
from employee.models import Employee, Department

User = get_user_model()

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.ChoiceField(choices=['M', 'F', 'O'], required=False)
    dob = serializers.DateField(required=False)
    phone = serializers.CharField(required=False)
    current_address = serializers.CharField(required=False)
    permanent_address = serializers.CharField(required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)
    position = serializers.CharField(required=False)
    date_of_joining = serializers.DateTimeField(required=False)
    role = serializers.ChoiceField(
        choices=[
            (1, 'HR'),
            (2, 'Project Manager'),
            (3, 'Team Lead'),
            (4, 'Employee'),
            (5, 'Admin')
        ],
        default=4
    )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already in use")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role', 4)

        # Create User
        user = User.objects.create_user(
            username=validated_data['email'],  # required by Django
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Create Employee profile
        employee = Employee.objects.create(
            user=user,
            role=role,
            gender=validated_data.get('gender'),
            dob=validated_data.get('dob'),
            phone=validated_data.get('phone'),
            current_address=validated_data.get('current_address', ''),
            permanent_address=validated_data.get('permanent_address', ''),
            department=validated_data.get('department'),
            position=validated_data.get('position', ''),
            date_of_joining=validated_data.get('date_of_joining')
        )

        return employee


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)