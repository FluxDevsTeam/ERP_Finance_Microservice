from rest_framework import serializers
from .models import Account, BalanceSwitchLog
from datetime import date


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')


class BalanceSwitchLogSerializer(serializers.ModelSerializer):
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)

    class Meta:
        model = BalanceSwitchLog
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by', 'created_at', 'updated_at')

    def validate(self, attrs):
        from_account = attrs.get('from_account')
        to_account = attrs.get('to_account')
        amount = attrs.get('amount')
        switch_date = attrs.get('switch_date', date.today())

        if from_account == to_account:
            raise serializers.ValidationError("Source and destination accounts must be different.")
        if from_account.tenant != to_account.tenant or from_account.branch != to_account.branch:
            raise serializers.ValidationError("Accounts must belong to the same tenant and branch.")
        if amount <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        if switch_date > date.today():
            raise serializers.ValidationError("Switch date cannot be in the future.")

        if from_account.balance < amount:
            raise serializers.ValidationError(
                f"Insufficient balance in {from_account.name} ({from_account.balance}) for transfer of {amount}."
            )

        return attrs