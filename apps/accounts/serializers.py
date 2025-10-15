from rest_framework import serializers
from .models import Account, AccountCategory, AccountTransaction


class AccountCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountCategory
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')


class AccountSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('balance', 'tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')


class AccountTransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = AccountTransaction
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')