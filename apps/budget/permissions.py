from rest_framework import permissions


class IsBudgetOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a budget to view/edit it.
    """

    def has_permission(self, request, view):
        return request.tenant_id is not None

    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.tenant_id and obj.branch == request.branch_id


class CanApproveBudget(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to approve budgets.
    """

    def has_permission(self, request, view):
        if not request.user:
            return False
        # Check if user has budget approval permission
        # This should be integrated with your role-based access control system
        return True  # Implement proper role checking