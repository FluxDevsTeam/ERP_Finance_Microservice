from rest_framework import permissions


class IsAssetOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an asset to view/edit it.
    """

    def has_permission(self, request, view):
        return request.tenant_id is not None

    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.tenant_id and obj.branch == request.branch_id