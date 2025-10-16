from django.contrib import admin
from .models import IncomeCategory, Income

@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'tenant', 'branch', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'tenant', 'branch')

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'account', 'amount', 'status', 'tenant', 'branch', 'created_at', 'updated_at')
    search_fields = ('reference', 'description')
    list_filter = ('status', 'tenant', 'branch')