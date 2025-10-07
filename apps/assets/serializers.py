from rest_framework import serializers
from .models import AssetCategory, Asset, AssetDisposal
from apps.accounts.serializers import AccountSerializer


class AssetCategorySerializer(serializers.ModelSerializer):
    asset_account_details = AccountSerializer(source='asset_account', read_only=True)
    depreciation_account_details = AccountSerializer(source='depreciation_account', read_only=True)
    accumulated_depreciation_account_details = AccountSerializer(
        source='accumulated_depreciation_account', read_only=True
    )
    
    class Meta:
        model = AssetCategory
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')


class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    depreciation_method_display = serializers.CharField(
        source='get_depreciation_method_display', read_only=True
    )
    
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at', 'current_value',
                          'last_depreciation_date')


class AssetDisposalSerializer(serializers.ModelSerializer):
    asset_details = AssetSerializer(source='asset', read_only=True)
    
    class Meta:
        model = AssetDisposal
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')