from rest_framework import permissions


class IsJournalEntryOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a journal entry to view/edit it.
    """

    def has_permission(self, request, view):
        return request.tenant_id is not None

    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.tenant_id and obj.branch == request.branch_id