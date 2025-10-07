from rest_framework import serializers
from .models import (
    Document, DocumentVersion, DocumentWorkflow,
    DocumentAccess, DocumentComment, DocumentAudit
)

class DocumentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    current_user_access = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('organization', 'version')

    def get_current_user_access(self, obj):
        request = self.context.get('request')
        if request and request.user:
            try:
                access = obj.access_controls.get(user=request.user)
                return access.access_level
            except DocumentAccess.DoesNotExist:
                return None
        return None

class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentVersion
        fields = '__all__'
        read_only_fields = ('organization', 'created_by')

class DocumentWorkflowSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    assignee_names = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()

    class Meta:
        model = DocumentWorkflow
        fields = '__all__'
        read_only_fields = ('organization',)

    def get_assignee_names(self, obj):
        return [user.get_full_name() for user in obj.assignees.all()]

    def get_total_steps(self, obj):
        return len(obj.steps)

class DocumentAccessSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentAccess
        fields = '__all__'
        read_only_fields = ('organization',)

class DocumentCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentComment
        fields = '__all__'
        read_only_fields = ('organization', 'user', 'resolved_by', 'resolved_at')

class DocumentAuditSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = DocumentAudit
        fields = '__all__'
        read_only_fields = ('organization',)