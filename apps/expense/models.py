from django.db import models
from apps.accounts.models import Account


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT,
                              limit_choices_to={'category__type': 'expense'})
    requires_approval = models.BooleanField(default=False)
    approval_threshold = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
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
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_date = models.DateField(null=True, blank=True)
    
    # Approval Information
    approved_by = models.UUIDField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
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
            date=self.payment_date or self.date,
            reference=f"EXP-{self.reference}",
            description=f"Expense: {self.description}",
            tenant=self.tenant,
            branch=self.branch,
            created_by=self.created_by
        )

        # Create debit line (expense account)
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=self.category.account,
            type='debit',
            amount=self.amount,
            description=self.description,
            tenant=self.tenant,
            branch=self.branch
        )

        # Create credit line (usually cash/bank account)
        cash_account = Account.objects.get(code='1001')  # Default cash account
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=cash_account,
            type='credit',
            amount=self.amount,
            description=self.description,
            tenant=self.tenant,
            branch=self.branch
        )

        return journal_entry

    def submit_for_approval(self):
        if self.status != 'draft':
            raise ValueError("Only draft expenses can be submitted for approval")
        
        if self.category.requires_approval and self.amount >= self.category.approval_threshold:
            self.status = 'pending_approval'
        else:
            self.status = 'approved'
        self.save()

    def approve(self, approver_id):
        if self.status != 'pending_approval':
            raise ValueError("Only pending expenses can be approved")
        
        self.status = 'approved'
        self.approved_by = approver_id
        self.save()

    def reject(self, approver_id, reason):
        if self.status != 'pending_approval':
            raise ValueError("Only pending expenses can be rejected")
        
        self.status = 'rejected'
        self.approved_by = approver_id
        self.rejection_reason = reason
        self.save()

    def mark_as_paid(self):
        if self.status != 'approved':
            raise ValueError("Only approved expenses can be marked as paid")
        
        journal_entry = self.create_journal_entry()
        journal_entry.post()
        
        self.status = 'paid'
        self.payment_date = journal_entry.date
        self.save()