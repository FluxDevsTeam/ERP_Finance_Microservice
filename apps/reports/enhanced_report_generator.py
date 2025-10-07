from django.db import models
from django.db.models import Sum, Q, F, Value, Count, Case, When
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from decimal import Decimal
from apps.accounts.models import Account, AccountTransaction
from apps.journal.models import JournalEntry, JournalLine
from apps.income.models import Income
from apps.expense.models import Expense
from apps.budget.models import Budget, BudgetItem
from apps.assets.models import Asset


class ReportGenerator:
    """Enhanced Report Generator with additional financial reports"""
    
    def __init__(self, tenant_id, branch_id, start_date=None, end_date=None):
        self.tenant_id = tenant_id
        self.branch_id = branch_id
        self.start_date = start_date or timezone.now().date()
        self.end_date = end_date or timezone.now().date()
        
    def get_budget_variance(self):
        """Generate budget variance report"""
        budgets = Budget.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            year=self.end_date.year,
            status='active'
        )
        
        variance_data = []
        for budget in budgets:
            items = BudgetItem.objects.filter(budget=budget)
            for item in items:
                actual_amount = AccountTransaction.objects.filter(
                    account=item.account,
                    date__range=[self.start_date, self.end_date],
                    tenant=self.tenant_id,
                    branch=self.branch_id
                ).aggregate(total=Sum('amount'))['total'] or 0

                variance = actual_amount - item.amount
                variance_percentage = (variance / item.amount * 100) if item.amount != 0 else 0

                variance_data.append({
                    'account': item.account.name,
                    'budgeted': float(item.amount),
                    'actual': float(actual_amount),
                    'variance': float(variance),
                    'variance_percentage': float(variance_percentage)
                })
                
        return variance_data

    def get_expense_analysis(self):
        """Generate expense analysis report"""
        expenses = Expense.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            date__range=[self.start_date, self.end_date],
            status='paid'
        ).values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg_amount=Sum('amount') / Count('id')
        ).order_by('-total')
        
        monthly_trend = Expense.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            date__range=[self.start_date, self.end_date],
            status='paid'
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        return {
            'summary': list(expenses),
            'monthly_trend': list(monthly_trend)
        }

    def get_revenue_analysis(self):
        """Generate revenue analysis report"""
        revenues = Income.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            date__range=[self.start_date, self.end_date],
            status='confirmed'
        ).values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg_amount=Sum('amount') / Count('id')
        ).order_by('-total')
        
        monthly_trend = Income.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            date__range=[self.start_date, self.end_date],
            status='confirmed'
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        return {
            'summary': list(revenues),
            'monthly_trend': list(monthly_trend)
        }

    def get_tax_report(self):
        """Generate tax report"""
        tax_accounts = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__code__startswith='2200'  # Assuming tax accounts start with 2200
        )
        
        tax_data = []
        for account in tax_accounts:
            transactions = AccountTransaction.objects.filter(
                account=account,
                date__range=[self.start_date, self.end_date]
            )
            
            tax_data.append({
                'tax_type': account.name,
                'collected': float(transactions.filter(type='credit').aggregate(total=Sum('amount'))['total'] or 0),
                'paid': float(transactions.filter(type='debit').aggregate(total=Sum('amount'))['total'] or 0),
                'balance': float(account.balance)
            })
            
        return tax_data

    def get_bank_reconciliation(self):
        """Generate bank reconciliation report"""
        bank_accounts = Account.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            category__code__startswith='1010'  # Assuming bank accounts start with 1010
        )
        
        reconciliation_data = []
        for account in bank_accounts:
            transactions = AccountTransaction.objects.filter(
                account=account,
                date__range=[self.start_date, self.end_date]
            ).order_by('date')
            
            reconciliation_data.append({
                'account_name': account.name,
                'opening_balance': float(account.balance - sum(t.amount if t.type == 'debit' else -t.amount for t in transactions)),
                'deposits': float(transactions.filter(type='debit').aggregate(total=Sum('amount'))['total'] or 0),
                'withdrawals': float(transactions.filter(type='credit').aggregate(total=Sum('amount'))['total'] or 0),
                'closing_balance': float(account.balance),
                'transactions': [{
                    'date': t.date,
                    'reference': t.reference,
                    'description': t.description,
                    'amount': float(t.amount),
                    'type': t.type
                } for t in transactions]
            })
            
        return reconciliation_data

    def get_department_pl(self):
        """Generate departmental profit & loss report"""
        departments = ['sales', 'production', 'admin', 'marketing']  # Example departments
        department_data = {}
        
        for dept in departments:
            revenues = Income.objects.filter(
                tenant=self.tenant_id,
                branch=self.branch_id,
                date__range=[self.start_date, self.end_date],
                status='confirmed',
                metadata__department=dept
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            expenses = Expense.objects.filter(
                tenant=self.tenant_id,
                branch=self.branch_id,
                date__range=[self.start_date, self.end_date],
                status='paid',
                metadata__department=dept
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            department_data[dept] = {
                'revenue': float(revenues),
                'expenses': float(expenses),
                'profit_loss': float(revenues - expenses)
            }
            
        return department_data

    def get_project_costing(self):
        """Generate project costing report"""
        project_transactions = JournalEntry.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id,
            date__range=[self.start_date, self.end_date],
            metadata__project_id__isnull=False
        ).values('metadata__project_id', 'metadata__project_name').annotate(
            total_cost=Sum(
                Case(
                    When(journalline__account__category__type='expense', then='journalline__amount'),
                    default=Value(0),
                    output_field=models.DecimalField()
                )
            ),
            total_revenue=Sum(
                Case(
                    When(journalline__account__category__type='revenue', then='journalline__amount'),
                    default=Value(0),
                    output_field=models.DecimalField()
                )
            )
        )
        
        for project in project_transactions:
            project['profit_loss'] = float(project['total_revenue'] - project['total_cost'])
            project['margin_percentage'] = (
                float(project['profit_loss'] / project['total_revenue'] * 100)
                if project['total_revenue'] != 0 else 0
            )
            
        return list(project_transactions)

    def get_fixed_assets_register(self):
        """Generate fixed assets register report"""
        assets = Asset.objects.filter(
            tenant=self.tenant_id,
            branch=self.branch_id
        ).select_related('category')
        
        register_data = []
        for asset in assets:
            accumulated_depreciation = (
                asset.purchase_cost - asset.current_value
                if asset.status == 'active' else
                asset.purchase_cost
            )
            
            register_data.append({
                'asset_number': asset.asset_number,
                'name': asset.name,
                'category': asset.category.name,
                'purchase_date': asset.purchase_date,
                'purchase_cost': float(asset.purchase_cost),
                'current_value': float(asset.current_value),
                'accumulated_depreciation': float(accumulated_depreciation),
                'depreciation_method': asset.get_depreciation_method_display(),
                'status': asset.get_status_display(),
                'last_depreciation_date': asset.last_depreciation_date
            })
            
        return register_data