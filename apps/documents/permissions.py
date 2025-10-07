from rest_framework import permissions
from .models import DocumentAccess

class HasDocumentAccess(permissions.BasePermission):
    """
    Custom permission to check if user has appropriate access level to the document.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Superusers and document admins have full access
        if user.has_perm('documents.manage_all_documents'):
            return True

        # Document owners have full access to their documents
        if hasattr(obj, 'document'):
            document = obj.document
        else:
            document = obj

        if document.owner == user:
            return True

        try:
            access = DocumentAccess.objects.get(document=document, user=user)
            if request.method in permissions.SAFE_METHODS:
                return access.access_level in ['VIE', 'EDI', 'APP', 'FUL']
            return access.access_level in ['EDI', 'APP', 'FUL']
        except DocumentAccess.DoesNotExist:
            return False

class IsDocumentOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a document or admins to manage it.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Allow if user is a document admin
        if user.has_perm('documents.manage_all_documents'):
            return True

        # Check if user is the document owner
        if hasattr(obj, 'document'):
            return obj.document.owner == user
        return obj.owner == user

class CanManageWorkflow(permissions.BasePermission):
    """
    Custom permission to check if user can manage document workflows.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow if user is a workflow admin
        if user.has_perm('documents.manage_all_workflows'):
            return True

        # Allow if user is document owner
        if obj.document.owner == user:
            return True

        # Allow if user is assigned to the workflow
        if obj.assignees.filter(id=user.id).exists():
            return True

        return False