from django.contrib import admin
from .models import JournalEntry, JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 2
    min_num = 2


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'reference', 'description', 'status', 'total_amount', 'tenant', 'branch')
    list_filter = ('status', 'date', 'tenant', 'branch')
    search_fields = ('reference', 'description')
    inlines = [JournalLineInline]
    date_hierarchy = 'date'