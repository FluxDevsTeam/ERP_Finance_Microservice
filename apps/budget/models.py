from django.db import models
from django.core.validators import MinValueValidator
from apps.accounts.models import Account


class Budget(models.Model):
    PERIOD_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('year', 'period', 'tenant', 'branch')
        ordering = ['-year', 'period']

    def __str__(self):
        return f"{self.name} - {self.year} ({self.get_period_display()})"


class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    period_num = models.PositiveIntegerField()  # 1-12 for monthly, 1-4 for quarterly, 1 for annual
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()

    class Meta:
        unique_together = ('budget', 'account', 'period_num')
        ordering = ['period_num', 'account']

    def __str__(self):
        return f"{self.budget.name} - {self.account.name} - Period {self.period_num}"


class BudgetVariance(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='variances')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    period_num = models.PositiveIntegerField()
    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2)
    variance_amount = models.DecimalField(max_digits=15, decimal_places=2)
    variance_percentage = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('budget', 'account', 'period_num')
        ordering = ['period_num', 'account']

    def __str__(self):
        return f"{self.budget.name} - {self.account.name} - Period {self.period_num}"

    def calculate_variance(self):
        """Calculate variance amount and percentage"""
        self.variance_amount = self.actual_amount - self.budgeted_amount
        if self.budgeted_amount != 0:
            self.variance_percentage = (self.variance_amount / self.budgeted_amount) * 100
        else:
            self.variance_percentage = 0 if self.actual_amount == 0 else 100