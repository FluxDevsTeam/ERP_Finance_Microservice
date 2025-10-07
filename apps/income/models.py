from django.db import models
from apps.accounts.models import Account


class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, 
                              limit_choices_to={'category__type': 'revenue'})
    is_active = models.BooleanField(default=True)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
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
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
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
        return f"{self.date} - {self.category.name} - {self.amount}"

    def create_journal_entry(self):
        from apps.journal.models import JournalEntry, JournalLine
        
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            date=self.date,
            reference=f"INC-{self.reference}",
            description=f"Income: {self.description}",
            tenant=self.tenant,
            branch=self.branch,
            created_by=self.created_by
        )

        # Create debit line (usually cash/bank account)
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=self.category.account,  # Revenue account
            type='credit',
            amount=self.amount,
            description=self.description,
            tenant=self.tenant,
            branch=self.branch
        )

        # Create credit line (income account)
        # Assuming there's a default asset account for income receipts
        cash_account = Account.objects.get(code='1001')  # Default cash account
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=cash_account,
            type='debit',
            amount=self.amount,
            description=self.description,
            tenant=self.tenant,
            branch=self.branch
        )

        return journal_entry

    def confirm(self):
        if self.status != 'draft':
            raise ValueError("Only draft incomes can be confirmed")
        
        journal_entry = self.create_journal_entry()
        journal_entry.post()
        
        self.status = 'confirmed'
        self.save()