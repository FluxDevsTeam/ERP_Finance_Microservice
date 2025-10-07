from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Income, IncomeCategory
from .serializers import IncomeSerializer, IncomeCategorySerializer
from .permissions import IsIncomeOwner


class IncomeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeCategorySerializer
    permission_classes = [IsAuthenticated, IsIncomeOwner]

    def get_queryset(self):
        return IncomeCategory.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )


class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated, IsIncomeOwner]

    def get_queryset(self):
        return Income.objects.filter(
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
    def confirm(self, request, pk=None):
        income = self.get_object()
        try:
            income.confirm()
            return Response({'status': 'Income entry confirmed successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)