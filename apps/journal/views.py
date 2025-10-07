from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import JournalEntry, JournalLine
from .serializers import JournalEntrySerializer, JournalLineSerializer
from .permissions import IsJournalEntryOwner


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated, IsJournalEntryOwner]

    def get_queryset(self):
        return JournalEntry.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )

    @action(detail=True, methods=['post'])
    def post_entry(self, request, pk=None):
        journal_entry = self.get_object()
        try:
            journal_entry.post()
            return Response({'status': 'Journal entry posted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)