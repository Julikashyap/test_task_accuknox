from rest_framework import permissions

class IsAdminOrReadOnlyParmission(permissions.BasePermission):
    """
    Custom permission to only allow admins to create, update, or delete groups.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow all users to view (GET) groups
        return request.user and request.user.is_staff  # Allow only admin users to create, update, or delete groups