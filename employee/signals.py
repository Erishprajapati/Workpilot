from .models import Employee, EmployeeProfile
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Employee)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile for the new employee
        EmployeeProfile.objects.create(employee=instance)