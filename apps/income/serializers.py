from rest_framework import serializers
from .models import Income, IncomeCategory
from apps.accounts.models import Account


class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')


class IncomeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')

    def validate(self, attrs):
        account = attrs.get('account')
        tenant = self.context['request'].tenant_id
        branch = self.context['request'].branch_id

        if account.tenant != tenant or account.branch != branch:
            raise serializers.ValidationError("Selected account must belong to the same tenant and branch.")
        if attrs.get('amount') <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        if attrs.get('date') > date.today():
            raise serializers.ValidationError("Income date cannot be in the future.")
        return attrs