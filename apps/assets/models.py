from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import Account


class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    useful_life_years = models.PositiveIntegerField()
    depreciation_method = models.CharField(
        max_length=20,
        choices=[
            ('straight_line', 'Straight Line'),
            ('reducing_balance', 'Reducing Balance'),
        ],
        default='straight_line'
    )
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Annual depreciation rate as percentage'
    )
    asset_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='asset_categories',
        limit_choices_to={'category__type': 'asset'}
    )
    depreciation_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='depreciation_categories',
        limit_choices_to={'category__type': 'expense'}
    )
    accumulated_depreciation_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='accumulated_depreciation_categories',
        limit_choices_to={'category__type': 'asset'}
    )
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
        unique_together = ('name', 'tenant')
        ordering = ['name']

    def __str__(self):
        return self.name


class Asset(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('disposed', 'Disposed'),
        ('written_off', 'Written Off'),
    )

    name = models.CharField(max_length=100)
    asset_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    useful_life_years = models.PositiveIntegerField()
    depreciation_method = models.CharField(max_length=20, choices=AssetCategory._meta.get_field('depreciation_method').choices)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2)
    last_depreciation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['asset_number']

    def __str__(self):
        return f"{self.asset_number} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # New asset
            self.current_value = self.purchase_cost
            if not self.useful_life_years:
                self.useful_life_years = self.category.useful_life_years
            if not self.depreciation_method:
                self.depreciation_method = self.category.depreciation_method
            if not self.depreciation_rate:
                self.depreciation_rate = self.category.depreciation_rate
        super().save(*args, **kwargs)

    def calculate_depreciation(self, date):
        """Calculate depreciation amount for a given date"""
        if self.status != 'active' or date <= (self.last_depreciation_date or self.purchase_date):
            return 0

        if self.depreciation_method == 'straight_line':
            annual_depreciation = (self.purchase_cost - self.salvage_value) / self.useful_life_years
            monthly_depreciation = annual_depreciation / 12
            return monthly_depreciation
        else:  # reducing_balance
            current_value = self.current_value
            monthly_rate = self.depreciation_rate / 12 / 100
            return current_value * monthly_rate

    def record_depreciation(self, date, amount):
        """Record depreciation transaction"""
        from apps.journal.models import JournalEntry, JournalLine

        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            date=date,
            reference=f"DEP-{self.asset_number}-{date}",
            description=f"Depreciation for {self.name}",
            tenant=self.tenant,
            branch=self.branch,
            created_by=self.created_by
        )

        # Debit Depreciation Expense
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=self.category.depreciation_account,
            type='debit',
            amount=amount,
            description=f"Depreciation expense for {self.name}",
            tenant=self.tenant,
            branch=self.branch
        )

        # Credit Accumulated Depreciation
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=self.category.accumulated_depreciation_account,
            type='credit',
            amount=amount,
            description=f"Accumulated depreciation for {self.name}",
            tenant=self.tenant,
            branch=self.branch
        )

        # Update asset
        self.current_value -= amount
        self.last_depreciation_date = date
        self.save()

        return journal_entry


class AssetDisposal(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.PROTECT)
    date = models.DateField()
    sale_price = models.DecimalField(max_digits=15, decimal_places=2)
    costs_of_disposal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reason = models.TextField()
    
    # Integration with Identity Microservice
    tenant = models.UUIDField()
    branch = models.UUIDField()
    created_by = models.UUIDField()
    updated_by = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Disposal of {self.asset.name}"

    def record_disposal(self):
        """Record asset disposal transactions"""
        from apps.journal.models import JournalEntry, JournalLine

        # Calculate gain/loss
        net_sale_proceeds = self.sale_price - self.costs_of_disposal
        book_value = self.asset.current_value
        gain_loss = net_sale_proceeds - book_value

        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            date=self.date,
            reference=f"DISP-{self.asset.asset_number}",
            description=f"Disposal of {self.asset.name}",
            tenant=self.tenant,
            branch=self.branch,
            created_by=self.created_by
        )

        # Debit Cash/Bank for sale proceeds
        cash_account = Account.objects.get(code='1001')  # Default cash account
        if self.sale_price > 0:
            JournalLine.objects.create(
                journal_entry=journal_entry,
                account=cash_account,
                type='debit',
                amount=self.sale_price,
                description=f"Sale proceeds from {self.asset.name}",
                tenant=self.tenant,
                branch=self.branch
            )

        # Credit Asset account
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=self.asset.category.asset_account,
            type='credit',
            amount=self.asset.purchase_cost,
            description=f"Remove asset cost for {self.asset.name}",
            tenant=self.tenant,
            branch=self.branch
        )

        # Debit Accumulated Depreciation
        accumulated_depreciation = self.asset.purchase_cost - self.asset.current_value
        if accumulated_depreciation > 0:
            JournalLine.objects.create(
                journal_entry=journal_entry,
                account=self.asset.category.accumulated_depreciation_account,
                type='debit',
                amount=accumulated_depreciation,
                description=f"Remove accumulated depreciation for {self.asset.name}",
                tenant=self.tenant,
                branch=self.branch
            )

        # Record gain/loss
        if gain_loss != 0:
            gain_loss_account = Account.objects.get(
                code='8001' if gain_loss > 0 else '8002'
            )  # Gain/Loss on disposal accounts
            JournalLine.objects.create(
                journal_entry=journal_entry,
                account=gain_loss_account,
                type='credit' if gain_loss > 0 else 'debit',
                amount=abs(gain_loss),
                description=f"{'Gain' if gain_loss > 0 else 'Loss'} on disposal of {self.asset.name}",
                tenant=self.tenant,
                branch=self.branch
            )

        # Update asset status
        self.asset.status = 'disposed'
        self.asset.save()

        return journal_entry
