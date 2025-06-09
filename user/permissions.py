from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow users with role 'Teacher' to create .
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Teacher'


from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Faqat  yaratuvchisiga (owner) ruxsat beriladi.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user