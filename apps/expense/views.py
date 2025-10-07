from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer
from .permissions import IsExpenseOwner, CanApproveExpense


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated, IsExpenseOwner]

    def get_queryset(self):
        return ExpenseCategory.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsExpenseOwner]

    def get_queryset(self):
        queryset = Expense.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        expense = self.get_object()
        try:
            expense.submit_for_approval()
            return Response({'status': 'Expense submitted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[CanApproveExpense])
    def approve(self, request, pk=None):
        expense = self.get_object()
        try:
            expense.approve(request.user.id)
            return Response({'status': 'Expense approved successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[CanApproveExpense])
    def reject(self, request, pk=None):
        expense = self.get_object()
        reason = request.data.get('reason', '')
        if not reason:
            return Response({'error': 'Rejection reason is required'},
                          status=status.HTTP_400_BAD_REQUEST)
        try:
            expense.reject(request.user.id, reason)
            return Response({'status': 'Expense rejected successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        expense = self.get_object()
        try:
            expense.mark_as_paid()
            return Response({'status': 'Expense marked as paid successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)