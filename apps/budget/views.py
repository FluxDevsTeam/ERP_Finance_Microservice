from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Budget, BudgetItem, BudgetVariance
from .serializers import BudgetSerializer, BudgetItemSerializer, BudgetVarianceSerializer
from .permissions import IsBudgetOwner, CanApproveBudget
from apps.accounts.models import AccountTransaction


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsBudgetOwner]

    def get_queryset(self):
        return Budget.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )

    @action(detail=True, methods=['post'], permission_classes=[CanApproveBudget])
    def approve(self, request, pk=None):
        budget = self.get_object()
        if budget.status != 'draft':
            return Response(
                {'error': 'Only draft budgets can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.status = 'approved'
        budget.updated_by = request.user.id
        budget.save()
        
        return Response({'status': 'Budget approved successfully'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        budget = self.get_object()
        if budget.status != 'approved':
            return Response(
                {'error': 'Only approved budgets can be activated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.status = 'active'
        budget.updated_by = request.user.id
        budget.save()
        
        return Response({'status': 'Budget activated successfully'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        budget = self.get_object()
        if budget.status != 'active':
            return Response(
                {'error': 'Only active budgets can be closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.status = 'closed'
        budget.updated_by = request.user.id
        budget.save()
        
        return Response({'status': 'Budget closed successfully'})


class BudgetItemViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetItemSerializer
    permission_classes = [IsAuthenticated, IsBudgetOwner]

    def get_queryset(self):
        return BudgetItem.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )


class BudgetVarianceViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetVarianceSerializer
    permission_classes = [IsAuthenticated, IsBudgetOwner]

    def get_queryset(self):
        return BudgetVariance.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        instance = serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )
        instance.calculate_variance()
        instance.save()

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        variance = self.get_object()
        
        # Get actual amount from transactions
        actual_amount = AccountTransaction.objects.filter(
            account=variance.account,
            date__year=variance.budget.year,
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        ).aggregate(total=Sum('amount'))['total'] or 0

        variance.actual_amount = actual_amount
        variance.calculate_variance()
        variance.save()
        
        serializer = self.get_serializer(variance)
        return Response(serializer.data)