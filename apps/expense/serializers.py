from rest_framework import serializers
from .models import Expense, ExpenseCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at', 'approved_by', 'approved_at',
                          'payment_date')