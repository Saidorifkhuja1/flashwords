from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow users with role 'Teacher' to create a quiz.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Teacher'


