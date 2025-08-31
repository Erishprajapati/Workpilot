from rest_framework import permissions
from employee.models import * 

class IsAssignedEmployeeOrReviewer(permissions.BasePermission):
    """
    - Assigned employee can submit task for review (status='review')
    - PM/Team lead/HR can approve or mark as completed
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user == obj.assigned_to.user and request.data .get('status') == 'review':
            return True
        
        if request.user.role in ['PROJECT_MANAGER', 'TEAM_LEAD', 'HR', 'ADMIN']:
            return True
        
        return False