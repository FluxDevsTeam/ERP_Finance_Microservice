from django.contrib import admin
from .models import Account, AccountCategory, AccountTransaction


@admin.register(AccountCategory)
class AccountCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'tenant', 'branch')
    list_filter = ('type', 'tenant', 'branch')
    search_fields = ('name', 'code')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'balance', 'tenant', 'branch')
    list_filter = ('category', 'tenant', 'branch')
    search_fields = ('name', 'code')


@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'type', 'amount', 'reference', 'tenant', 'branch')
    list_filter = ('type', 'account', 'tenant', 'branch')
    search_fields = ('reference', 'description')
    date_hierarchy = 'date'