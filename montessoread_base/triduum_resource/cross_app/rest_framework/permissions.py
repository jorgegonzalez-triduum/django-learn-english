from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class DjangoPermissions(permissions.BasePermission):
    """
    Global permission check for django permissions.
    """

    def has_permission(self, request, view):
        if view.permissions_required:
            return view.request.user.has_perms(view.permissions_required)
        else:
            return True