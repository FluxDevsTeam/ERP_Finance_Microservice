from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import Account


class JournalEntry(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    )

    date = models.DateField()
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'

    def __str__(self):
        return f"{self.date} - {self.reference}"

    def clean(self):
        if self.journalline_set.count() < 2:
            raise ValidationError(_('Journal entry must have at least two lines'))
        
        total_debit = sum(line.amount for line in self.journalline_set.filter(type='debit'))
        total_credit = sum(line.amount for line in self.journalline_set.filter(type='credit'))
        
        if total_debit != total_credit:
            raise ValidationError(_('Total debit must equal total credit'))

    def post(self):
        if self.status != 'draft':
            raise ValidationError(_('Only draft entries can be posted'))
        
        self.clean()
        for line in self.journalline_set.all():
            line.post()
        
        self.status = 'posted'
        self.save()


class JournalLine(models.Model):
    ENTRY_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    )

    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.account.name} - {self.type} {self.amount}"

    def clean(self):
        if not self.tenant:
            self.tenant = self.journal_entry.tenant
        if not self.branch:
            self.branch = self.journal_entry.branch
        
        if self.tenant != self.account.tenant:
            raise ValidationError(_('Account does not belong to the same tenant'))
        if self.branch != self.account.branch:
            raise ValidationError(_('Account does not belong to the same branch'))

    def post(self):
        """
        Post the journal line to update account balance
        """
        self.account.update_balance(self.amount, self.type)