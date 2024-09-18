# permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    """
    Full access for users in the 'admin' group.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='admin').exists()

class IsWrite(BasePermission):
    """
    Allows GET (read) and POST/PUT/PATCH (write) methods, but forbids DELETE for users in the 'write' group.
    """
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return False  # Write users should not be able to delete
        return request.user and request.user.groups.filter(name='write').exists()

class IsRead(BasePermission):
    """
    Only allows read access for users in the 'read' group (GET).
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='read').exists() and request.method in SAFE_METHODS
