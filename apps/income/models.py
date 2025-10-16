from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import Account


class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Income Category'
        verbose_name_plural = 'Income Categories'
        unique_together = ('name', 'tenant')
        ordering = ['name']

    def __str__(self):
        return self.name


class Income(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    date = models.DateField()
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
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
        return f"{self.date} - {self.category.name} - {self.amount} to {self.account.name}"

    def clean(self):
        if self.account.tenant != self.tenant or self.account.branch != self.branch:
            raise ValidationError("Selected account must belong to the same tenant and branch.")
        if self.amount <= 0:
            raise ValidationError("Amount must be positive.")

    def confirm(self):
        if self.status != 'draft':
            raise ValidationError("Only draft income entries can be confirmed.")
        self.status = 'confirmed'
        self.account.balance += self.amount
        self.account.save()
        self.save()
