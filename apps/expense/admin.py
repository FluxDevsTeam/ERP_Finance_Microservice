from django.contrib import admin
from .models import ExpenseCategory, Expense

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'requires_approval', 'approval_threshold', 'is_active', 'tenant', 'branch', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('requires_approval', 'is_active', 'tenant', 'branch')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'account', 'amount', 'status', 'tenant', 'branch', 'created_at', 'updated_at')
    search_fields = ('reference', 'description')
    list_filter = ('status', 'tenant', 'branch')