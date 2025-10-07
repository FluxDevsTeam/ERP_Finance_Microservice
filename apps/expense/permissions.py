from rest_framework import permissions


class IsExpenseOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an expense to view/edit it.
    """

    def has_permission(self, request, view):
        return request.tenant_id is not None

    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.tenant_id and obj.branch == request.branch_id


class CanApproveExpense(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to approve expenses.
    """

    def has_permission(self, request, view):
        if not request.user:
            return False
        # Check if user has approval permission
        # This should be integrated with your role-based access control system
        return True  # Implement proper role checking