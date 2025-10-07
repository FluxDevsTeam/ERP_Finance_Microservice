from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import (
    Document, DocumentVersion, DocumentWorkflow,
    DocumentAccess, DocumentComment, DocumentAudit
)
from .serializers import (
    DocumentSerializer, DocumentVersionSerializer,
    DocumentWorkflowSerializer, DocumentAccessSerializer,
    DocumentCommentSerializer, DocumentAuditSerializer
)
from .permissions import (
    HasDocumentAccess, IsDocumentOwnerOrAdmin,
    CanManageWorkflow
)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, HasDocumentAccess]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('documents.view_all_documents'):
            return self.queryset.filter(organization=user.organization)
        return self.queryset.filter(
            Q(organization=user.organization) &
            (Q(owner=user) | Q(access_controls__user=user))
        ).distinct()

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        document = self.get_object()
        document.status = 'ARC'
        document.save()
        return Response({'status': 'document archived'})

    @action(detail=True)
    def versions(self, request, pk=None):
        document = self.get_object()
        versions = document.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated, HasDocumentAccess]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DocumentWorkflowViewSet(viewsets.ModelViewSet):
    queryset = DocumentWorkflow.objects.all()
    serializer_class = DocumentWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkflow]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'due_date']

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('documents.manage_all_workflows'):
            return self.queryset.filter(organization=user.organization)
        return self.queryset.filter(
            Q(organization=user.organization) &
            (Q(document__owner=user) | Q(assignees=user))
        ).distinct()

    @action(detail=True, methods=['post'])
    def next_step(self, request, pk=None):
        workflow = self.get_object()
        if workflow.current_step < len(workflow.steps) - 1:
            workflow.current_step += 1
            workflow.save()
        return Response({
            'current_step': workflow.current_step,
            'is_complete': workflow.current_step == len(workflow.steps) - 1
        })

class DocumentAccessViewSet(viewsets.ModelViewSet):
    queryset = DocumentAccess.objects.all()
    serializer_class = DocumentAccessSerializer
    permission_classes = [permissions.IsAuthenticated, IsDocumentOwnerOrAdmin]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

class DocumentCommentViewSet(viewsets.ModelViewSet):
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated, HasDocumentAccess]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        comment = self.get_object()
        comment.resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        return Response({'status': 'comment resolved'})

class DocumentAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentAudit.objects.all()
    serializer_class = DocumentAuditSerializer
    permission_classes = [permissions.IsAuthenticated, IsDocumentOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)