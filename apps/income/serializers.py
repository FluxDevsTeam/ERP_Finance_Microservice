from rest_framework import serializers
from .models import Income, IncomeCategory


class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')


class IncomeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')