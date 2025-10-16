from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from .models import Income, IncomeCategory
from .serializers import IncomeSerializer, IncomeCategorySerializer
from rest_framework import serializers
from .utils import swagger_helper

class IncomeCategoryViewSet(viewsets.ModelViewSet):
    @swagger_helper("Income Categories", "Income Category")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_helper("Income Categories", "Income Category")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_helper("Income Categories", "Income Category")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_helper("Income Categories", "Income Category")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class IncomeViewSet(viewsets.ModelViewSet):
    @swagger_helper("Incomes", "Income")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_helper("Incomes", "Income")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_helper("Incomes", "Income")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_helper("Incomes", "Income")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_helper("Incomes", "Income")
    def perform_create(self, serializer):
        serializer.save()

    @swagger_helper("Incomes", "Income")
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status != 'draft':
            raise serializers.ValidationError("Only draft income entries can be updated.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status == 'confirmed':
            instance.account.balance -= instance.amount
            instance.account.save()
        instance.delete()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        income = self.get_object()
        try:
            income.confirm()
            return Response({'status': 'Income entry confirmed successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset().filter(status='confirmed')
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
                monthly_income = queryset.filter(date__year=year, date__month=m)
                if monthly_income.exists():
                    yearly_data.append({
                        'month': f"{year}-{m:02d}",
                        'total': float(monthly_income.aggregate(Sum('amount'))['amount__sum'] or 0.0),
                    })
            response_data['yearly_data'] = yearly_data
            response_data['yearly_total'] = float(queryset.filter(date__year=year).aggregate(Sum('amount'))['amount__sum'] or 0.0)

        return Response(response_data)

    @swagger_helper("Incomes", "Income")
    def destroy(self, request, *args, **kwargs):
        """
        Deletes an income instance.
        """
        return super().destroy(request, *args, **kwargs)

    @swagger_helper("Incomes", "Income")
    def update(self, request, *args, **kwargs):
        """
        Update method is not allowed for incomes.
        """
        return Response({"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)