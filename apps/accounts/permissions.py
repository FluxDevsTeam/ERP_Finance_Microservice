from rest_framework import permissions


class IsAccountOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an account to view/edit it.
    """

    def has_permission(self, request, view):
        # Check if user's tenant is present in request
        return request.tenant_id is not None

    def has_object_permission(self, request, view, obj):
        # Check if user's tenant matches the object's tenant
        return obj.tenant == request.tenant_id and obj.branch == request.branch_id