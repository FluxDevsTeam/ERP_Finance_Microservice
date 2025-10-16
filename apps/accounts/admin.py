from django.contrib import admin
from .models import Account, BalanceSwitchLog

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'balance', 'tenant', 'branch', 'created_at', 'updated_at')
    search_fields = ('name', 'account_type')
    list_filter = ('account_type', 'tenant', 'branch')

@admin.register(BalanceSwitchLog)
class BalanceSwitchLogAdmin(admin.ModelAdmin):
    list_display = ('from_account', 'to_account', 'amount', 'switch_date', 'tenant', 'branch', 'created_at', 'updated_at')
    search_fields = ('from_account__name', 'to_account__name')
    list_filter = ('switch_date', 'tenant', 'branch')