from django.db import models


class ReportTemplate(models.Model):
    REPORT_TYPES = (
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('cash_flow', 'Cash Flow Statement'),
        ('trial_balance', 'Trial Balance'),
        ('general_ledger', 'General Ledger'),
        ('accounts_receivable', 'Accounts Receivable Aging'),
        ('accounts_payable', 'Accounts Payable Aging'),
        ('budget_variance', 'Budget Variance Report'),
        ('expense_analysis', 'Expense Analysis'),
        ('revenue_analysis', 'Revenue Analysis'),
        ('tax_report', 'Tax Report'),
        ('bank_reconciliation', 'Bank Reconciliation'),
        ('department_pl', 'Departmental Profit & Loss'),
        ('project_costing', 'Project Costing Report'),
        ('inventory_valuation', 'Inventory Valuation'),
        ('fixed_assets', 'Fixed Assets Register'),
    )

    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    configuration = models.JSONField(default=dict)  # Store report-specific configuration
    is_active = models.BooleanField(default=True)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'tenant')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"


class GeneratedReport(models.Model):
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    parameters = models.JSONField(default=dict)  # Store parameters used to generate the report
    report_data = models.JSONField(default=dict)  # Store the generated report data
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.template.name} - {self.start_date} to {self.end_date}"