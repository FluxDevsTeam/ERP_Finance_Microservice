from rest_framework import serializers
from .models import Budget, BudgetItem, BudgetVariance
from apps.accounts.serializers import AccountSerializer


class BudgetItemSerializer(serializers.ModelSerializer):
    account_details = AccountSerializer(source='account', read_only=True)
    
    class Meta:
        model = BudgetItem
        fields = '__all__'
        read_only_fields = ('tenant', 'branch')


class BudgetVarianceSerializer(serializers.ModelSerializer):
    account_details = AccountSerializer(source='account', read_only=True)
    
    class Meta:
        model = BudgetVariance
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'variance_amount',
                          'variance_percentage', 'calculated_at')


class BudgetSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True, read_only=True)
    variances = BudgetVarianceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')