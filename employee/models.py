# employee/models.py

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

User = get_user_model()


"""
Abstract base class for shared fields
"""
class Timestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Department(models.Model):
    name = models.CharField(_('Name'), max_length=50, unique=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    department_code = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.department_code:
            prefix = self.name[:3].upper()
            last_count = Department.objects.count() + 1
            self.department_code = f"{prefix}{last_count:03d}"
        super().save(*args, **kwargs)


# Validator for Nepali phone numbers
nepali_phone_regex = RegexValidator(
    regex=r'^9[6-8]\d{8}$',
    message=_("Kindly enter valid phone numbers")
)


class EmployeeStatus(Timestamp):
    is_active = models.BooleanField(_('Status'), default=True)

    def __str__(self):
        return "Active" if self.is_active else "Inactive"


class Employee(Timestamp):
    GENDER_CHOICES = [
        ('M', "Male"),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Role choices
    HR = 1
    PROJECT_MANAGER = 2
    TEAM_LEAD = 3
    EMPLOYEE = 4
    ADMIN = 5

    ROLE_CHOICES = [
        (HR, 'HR'),
        (PROJECT_MANAGER, 'Project Manager'),
        (TEAM_LEAD, 'Team Lead'),
        (EMPLOYEE, 'Employee'),
        (ADMIN, 'Admin'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name='employee_profile',
        null=True,
        blank=True
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=EMPLOYEE)
    phone = models.CharField(_('Phone'), max_length=10, validators=[nepali_phone_regex], null=True, blank=True)
    dob = models.DateField(_('Date of birth'), null=True, blank=True)
    address = models.TextField(_('Address'), blank=True, null=True)
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    position = models.CharField(_('Position'), max_length=25, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    skills = models.JSONField(_('Skills'), default=list, blank=True)
    date_of_joining = models.DateTimeField(null=False, blank=False)  # Set at signup
    employee_status = models.ForeignKey(EmployeeStatus, on_delete=models.SET_NULL, blank=True, null=True)
    employee_code = models.CharField(
        max_length=255,
        unique=True,
        null=True,   # Critical: use NULL instead of "" to avoid unique constraint issues
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name() if self.user else f"Employee {self.id}"

    def save(self, *args, **kwargs):
        # Only generate code if not already set, and department/date are available
        if not self.employee_code and self.department and self.date_of_joining:
            with transaction.atomic():
                existing_count = Employee.objects.filter(
                    department=self.department,
                    date_of_joining__year=self.date_of_joining.year,
                    date_of_joining__month=self.date_of_joining.month,
                ).select_for_update().count()

                dept_code = self.department.name[:3].upper()
                date_part = self.date_of_joining.strftime("%Y%m")
                self.employee_code = f"{dept_code}-{date_part}-{existing_count + 1:03d}"

        super().save(*args, **kwargs)


class EmployeeProfile(Timestamp):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.FileField(upload_to='employee/profile/profile_photo/', null=True, blank=True)
    citizenship = models.FileField(upload_to='employee/profile/citizenship/', blank=True, null=True)
    contact_agreement = models.FileField(upload_to='employee/profile/contactagreement/', null=True, blank=True)

    def __str__(self):
        return str(self.employee)