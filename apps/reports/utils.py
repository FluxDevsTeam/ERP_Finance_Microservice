from django.db.models import Sum, Q
from django.utils import timezone
from apps.accounts.models import Account, AccountTransaction
from apps.journal.models import JournalEntry, JournalLine
from apps.income.models import Income
from apps.expense.models import Expense


class ReportGenerator:
    def __init__(self, tenant_id, branch_id, start_date=None, end_date=None):
        self.tenant_id = tenant_id
        self.branch_id = branch_id
        self.start_date = start_date or timezone.now().date()
        self.end_date = end_date or timezone.now().date()

    def get_balance_sheet(self):
        """Generate balance sheet report"""
        assets = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__type='asset'
        ).annotate(
            total_balance=Sum('balance')
        ).values('name', 'code', 'total_balance')

        liabilities = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__type='liability'
        ).annotate(
            total_balance=Sum('balance')
        ).values('name', 'code', 'total_balance')

        equity = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__type='equity'
        ).annotate(
            total_balance=Sum('balance')
        ).values('name', 'code', 'total_balance')

        return {
            'assets': list(assets),
            'liabilities': list(liabilities),
            'equity': list(equity),
        }

    def get_income_statement(self):
        """Generate income statement report"""
        revenues = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__type='revenue'
        ).annotate(
            total_amount=Sum('transactions__amount', 
                           filter=Q(transactions__date__range=[self.start_date, self.end_date]))
        ).values('name', 'code', 'total_amount')

        expenses = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__type='expense'
        ).annotate(
            total_amount=Sum('transactions__amount',
                           filter=Q(transactions__date__range=[self.start_date, self.end_date]))
        ).values('name', 'code', 'total_amount')

        return {
            'revenues': list(revenues),
            'expenses': list(expenses),
        }

    def get_cash_flow(self):
        """Generate cash flow statement"""
        operating_activities = JournalLine.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            journal_entry__date__range=[self.start_date, self.end_date],
            account__category__type__in=['revenue', 'expense']
        ).values(
            'account__name',
            'type'
        ).annotate(
            total_amount=Sum('amount')
        )

        investing_activities = JournalLine.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            journal_entry__date__range=[self.start_date, self.end_date],
            account__category__type='asset',
            account__code__startswith='15'  # Assuming fixed assets start with 15
        ).values(
            'account__name',
            'type'
        ).annotate(
            total_amount=Sum('amount')
        )

        financing_activities = JournalLine.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            journal_entry__date__range=[self.start_date, self.end_date],
            account__category__type__in=['liability', 'equity']
        ).values(
            'account__name',
            'type'
        ).annotate(
            total_amount=Sum('amount')
        )

        return {
            'operating_activities': list(operating_activities),
            'investing_activities': list(investing_activities),
            'financing_activities': list(financing_activities),
        }

    def get_trial_balance(self):
        """Generate trial balance report"""
        accounts = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id
        ).annotate(
            debit_balance=Sum('transactions__amount',
                            filter=Q(transactions__type='debit')),
            credit_balance=Sum('transactions__amount',
                             filter=Q(transactions__type='credit'))
        ).values('name', 'code', 'category__type', 'debit_balance', 'credit_balance')

        return {
            'accounts': list(accounts)
        }

    def get_accounts_aging(self, account_type='receivable'):
        """Generate accounts receivable/payable aging report"""
        today = timezone.now().date()
        accounts = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__type='asset' if account_type == 'receivable' else 'liability'
        )

        aging_data = []
        for account in accounts:
            transactions = AccountTransaction.objects.filter(
                account=account,
                date__lte=today
            ).order_by('date')

            aging_buckets = {
                'current': 0,
                '1_30': 0,
                '31_60': 0,
                '61_90': 0,
                'over_90': 0
            }

            for transaction in transactions:
                days_old = (today - transaction.date).days
                amount = transaction.amount if transaction.type == 'debit' else -transaction.amount

                if days_old <= 30:
                    aging_buckets['current'] += amount
                elif days_old <= 60:
                    aging_buckets['1_30'] += amount
                elif days_old <= 90:
                    aging_buckets['31_60'] += amount
                elif days_old <= 120:
                    aging_buckets['61_90'] += amount
                else:
                    aging_buckets['over_90'] += amount

            aging_data.append({
                'account': account.name,
                'code': account.code,
                'aging': aging_buckets
            })

        return aging_data