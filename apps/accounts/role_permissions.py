from rest_framework import permissions


class HasFinanceRole(permissions.BasePermission):
    """
    Permission class to check if user has required finance roles
    """
    
    def has_permission(self, request, view):
        # Always require authentication
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Get required roles for the view/action
        required_roles = getattr(view, 'required_roles', None)
        if not required_roles:
            return True  # No specific roles required
            
        # Check if user has any of the required roles
        user_roles = set(request.user.roles)
        return bool(user_roles & set(required_roles))


def finance_roles_required(*roles):
    """
    Decorator to specify required finance roles for views
    """
    def decorator(view_class):
        view_class.required_roles = roles
        return view_class
    return decorator