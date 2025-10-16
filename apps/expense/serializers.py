from rest_framework import serializers
from .models import Expense, ExpenseCategory
from apps.accounts.serializers import AccountSerializer

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'description', 'requires_approval', 'approval_threshold', 'is_active']
        read_only_fields = ['id']

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'date', 'category', 'category_name', 'account', 'account_name', 'amount',
            'description', 'reference', 'status', 'payment_date', 'approved_by',
            'approved_at', 'rejection_reason'
        ]
        read_only_fields = ['id', 'payment_date', 'approved_by', 'approved_at', 'rejection_reason']
        extra_kwargs = {'category': {'write_only': True}, 'account': {'write_only': True}}

    def validate(self, attrs):
        if attrs.get('amount') <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        if attrs.get('date') > date.today():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return attrs