from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import Account


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=False)
    approval_threshold = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        unique_together = ('name', 'tenant')
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    date = models.DateField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_date = models.DateField(null=True, blank=True)
    approved_by = models.UUIDField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ('reference', 'tenant', 'branch')

    def __str__(self):
        return f"{self.date} - {self.category.name} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Amount must be positive.")
