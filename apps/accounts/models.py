from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AccountCategory(models.Model):
    ACCOUNT_TYPES = (
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Account Category'
        verbose_name_plural = 'Account Categories'
        unique_together = ('code', 'tenant')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Account(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    category = models.ForeignKey(AccountCategory, on_delete=models.PROTECT, related_name='accounts')
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('code', 'tenant')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def update_balance(self, amount, transaction_type):
        """
        Update account balance based on transaction type
        """
        if transaction_type == 'debit':
            if self.category.type in ['asset', 'expense']:
                self.balance += amount
            else:
                self.balance -= amount
        else:  # credit
            if self.category.type in ['asset', 'expense']:
                self.balance -= amount
            else:
                self.balance += amount
        self.save()


class AccountTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    )

    date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    reference = models.CharField(max_length=100)
    description = models.TextField()
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.reference} ({self.amount})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only update balance on creation
            self.account.update_balance(self.amount, self.type)
        super().save(*args, **kwargs)