from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer
from django.db import transaction
from datetime import date
from .utils import swagger_helper

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseCategorySerializer
    queryset = ExpenseCategory.objects.all()

    @swagger_helper("Expense Categories", "Expense Category")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_helper("Expense Categories", "Expense Category")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_helper("Expense Categories", "Expense Category")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_helper("Expense Categories", "Expense Category")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()

    @swagger_helper("Expenses", "Expense")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_helper("Expenses", "Expense")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_helper("Expenses", "Expense")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_helper("Expenses", "Expense")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_helper("Expenses", "Expense")
    def perform_create(self, serializer):
        serializer.save()

    @swagger_helper("Expenses", "Expense")
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status not in ['draft', 'pending_approval']:
            raise serializers.ValidationError("Only draft or pending_approval expenses can be updated.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status == 'paid':
            instance.account.balance += instance.amount
            instance.account.save()
        instance.delete()

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        expense = self.get_object()
        try:
            expense.pay()
            return Response({'status': 'Expense marked as paid successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset().filter(status='paid')
        today = timezone.now().date()
        year = request.query_params.get('year', today.year)
        month = request.query_params.get('month', today.month)

        filtered = queryset.filter(date__year=year, date__month=month)
        monthly_total = filtered.aggregate(Sum('amount'))['amount__sum'] or 0.0
        cash_total = filtered.filter(account__account_type='CASH').aggregate(Sum('amount'))['amount__sum'] or 0.0
        bank_total = filtered.filter(account__account_type='BANK').aggregate(Sum('amount'))['amount__sum'] or 0.0
        debt_total = filtered.filter(account__account_type='DEBT').aggregate(Sum('amount'))['amount__sum'] or 0.0

        response_data = {
            'monthly_total': float(monthly_total),
            'cash_total': float(cash_total),
            'bank_total': float(bank_total),
            'debt_total': float(debt_total),
        }

        if year and not month:
            yearly_data = []
            for m in range(1, 13):
                monthly_expenses = queryset.filter(date__year=year, date__month=m)
                if monthly_expenses.exists():
                    yearly_data.append({
                        'month': f"{year}-{m:02d}",
                        'total': float(monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0.0),
                    })
            response_data['yearly_data'] = yearly_data
            response_data['yearly_total'] = float(queryset.filter(date__year=year).aggregate(Sum('amount'))['amount__sum'] or 0.0)

        return Response(response_data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)
        today = timezone.now().date()

        filtered = queryset
        monthly_total = filtered.filter(date__month=today.month, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0.0
        cash_total = filtered.filter(account__account_type='CASH', date__month=today.month, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0.0
        bank_total = filtered.filter(account__account_type='BANK', date__month=today.month, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0.0
        debt_total = filtered.filter(account__account_type='DEBT', date__month=today.month, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0.0

        if year and not month:
            yearly_data = []
            for m in range(1, 13):
                monthly_expenses = filtered.filter(date__year=year, date__month=m, status='paid')
                if monthly_expenses.exists():
                    entries = self.get_serializer(monthly_expenses, many=True).data
                    total_for_the_month = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0.0
                    yearly_data.append({
                        'month': f"{year}-{m:02d}",
                        'entries': entries,
                        'total_for_the_month': float(total_for_the_month),
                    })
            yearly_total = filtered.filter(date__year=year, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0.0
            response_data = {
                'monthly_total': float(monthly_total),
                'cash_total': float(cash_total),
                'bank_total': float(bank_total),
                'debt_total': float(debt_total),
                'yearly_data': yearly_data,
                'yearly_total': float(yearly_total),
            }
            return Response(response_data)

        if year is None and month is None:
            filtered = filtered.filter(date__year=today.year, date__month=today.month)
        if year is None and month is not None:
            filtered = filtered.filter(date__year=today.year, date__month=month)

        daily_data = []
        current_date = None
        daily_expenses = []
        for expense in filtered:
            expense_date = expense.date
            if expense_date != current_date:
                if daily_expenses:
                    daily_data.append({
                        'date': current_date,
                        'entries': self.get_serializer(daily_expenses, many=True).data,
                        'daily_total': float(sum(e.amount for e in daily_expenses)),
                    })
                current_date = expense_date
                daily_expenses = [expense]
            else:
                daily_expenses.append(expense)
        if daily_expenses:
            daily_data.append({
                'date': current_date,
                'entries': self.get_serializer(daily_expenses, many=True).data,
                'daily_total': float(sum(e.amount for e in daily_expenses)),
            })

        response_data = {
            'monthly_total': float(monthly_total),
            'cash_total': float(cash_total),
            'bank_total': float(bank_total),
            'debt_total': float(debt_total),
            'daily_data': daily_data,
        }
        if year:
            yearly_total = filtered.filter(date__year=year, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0.0
            response_data['yearly_total'] = float(yearly_total)

        return Response(response_data)