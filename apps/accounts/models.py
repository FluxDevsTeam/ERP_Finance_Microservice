from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import date


class Account(models.Model):
    ACCOUNT_TYPES = (
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
        ('DEBT', 'Debt'),
    )

    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        unique_together = ('name', 'tenant', 'branch')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.account_type}) - Tenant: {self.tenant}"

    def clean(self):
        if self.balance < 0:
            raise ValidationError("Account balance cannot be negative.")


class BalanceSwitchLog(models.Model):
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
        ('DEBT', 'Debt'),
    )

    from_account = models.ForeignKey(Account, related_name='from_switches', on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, related_name='to_switches', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    switch_date = models.DateField(default=date.today)
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Balance Switch Log'
        verbose_name_plural = 'Balance Switch Logs'
        ordering = ['-switch_date']

    def __str__(self):
        return f"Switch from {self.from_account} to {self.to_account} ({self.amount}) on {self.switch_date}"

    def clean(self):
        if self.from_account == self.to_account:
            raise ValidationError("Source and destination accounts must be different.")
        if self.from_account.tenant != self.to_account.tenant or self.from_account.branch != self.to_account.branch:
            raise ValidationError("Accounts must belong to the same tenant and branch.")
        if self.amount <= 0:
            raise ValidationError("Switch amount must be positive.")