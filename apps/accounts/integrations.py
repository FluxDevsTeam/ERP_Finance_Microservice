from decimal import Decimal
from typing import Dict, Optional
from django.utils import timezone
from .base import BaseFinancialIntegration, FinancialTransactionRequest
from apps.accounts.models import Account


class ProcurementIntegration(BaseFinancialIntegration):
    """Handles financial integration for procurement module"""

    def get_debit_account(self, transaction: FinancialTransactionRequest) -> Account:
        # For purchases, debit goes to inventory or asset account based on metadata
        if transaction.metadata.get('item_type') == 'asset':
            return Account.objects.get(code='1500')  # Fixed Assets
        else:
            return Account.objects.get(code='1200')  # Inventory

    def get_credit_account(self, transaction: FinancialTransactionRequest) -> Account:
        # Credit always goes to Accounts Payable for purchases
        return Account.objects.get(code='2000')  # Accounts Payable

    def record_purchase(
        self,
        amount: Decimal,
        reference: str,
        description: str,
        created_by: str,
        item_type: str = 'inventory',
        metadata: Optional[Dict] = None
    ) -> None:
        """Record a purchase transaction"""
        transaction = FinancialTransactionRequest(
            date=timezone.now().date(),
            description=description,
            amount=amount,
            reference=reference,
            source_module='PROC',
            tenant_id=self.tenant_id,
            branch_id=self.branch_id,
            created_by=created_by,
            metadata={'item_type': item_type, **(metadata or {})}
        )
        
        self.validate_transaction(transaction)
        return self.create_transaction(transaction)


class HRIntegration(BaseFinancialIntegration):
    """Handles financial integration for HR module"""

    def get_debit_account(self, transaction: FinancialTransactionRequest) -> Account:
        # For payroll, debit goes to appropriate expense account based on metadata
        transaction_type = transaction.metadata.get('type', 'salary')
        account_codes = {
            'salary': '5000',  # Salary Expense
            'overtime': '5001',  # Overtime Expense
            'bonus': '5002',  # Bonus Expense
            'commission': '5003',  # Commission Expense
        }
        return Account.objects.get(code=account_codes[transaction_type])

    def get_credit_account(self, transaction: FinancialTransactionRequest) -> Account:
        # Credit goes to payable account for payroll
        return Account.objects.get(code='2001')  # Payroll Payable

    def record_payroll(
        self,
        amount: Decimal,
        reference: str,
        description: str,
        created_by: str,
        payment_type: str = 'salary',
        metadata: Optional[Dict] = None
    ) -> None:
        """Record a payroll transaction"""
        transaction = FinancialTransactionRequest(
            date=timezone.now().date(),
            description=description,
            amount=amount,
            reference=reference,
            source_module='HR',
            tenant_id=self.tenant_id,
            branch_id=self.branch_id,
            created_by=created_by,
            metadata={'type': payment_type, **(metadata or {})}
        )
        
        self.validate_transaction(transaction)
        return self.create_transaction(transaction)


class SalesIntegration(BaseFinancialIntegration):
    """Handles financial integration for sales module"""

    def get_debit_account(self, transaction: FinancialTransactionRequest) -> Account:
        # For sales, debit goes to Accounts Receivable or Cash based on payment method
        payment_method = transaction.metadata.get('payment_method', 'credit')
        if payment_method == 'cash':
            return Account.objects.get(code='1001')  # Cash
        else:
            return Account.objects.get(code='1100')  # Accounts Receivable

    def get_credit_account(self, transaction: FinancialTransactionRequest) -> Account:
        # Credit goes to Sales Revenue
        return Account.objects.get(code='4000')  # Sales Revenue

    def record_sale(
        self,
        amount: Decimal,
        reference: str,
        description: str,
        created_by: str,
        payment_method: str = 'credit',
        metadata: Optional[Dict] = None
    ) -> None:
        """Record a sales transaction"""
        transaction = FinancialTransactionRequest(
            date=timezone.now().date(),
            description=description,
            amount=amount,
            reference=reference,
            source_module='SALES',
            tenant_id=self.tenant_id,
            branch_id=self.branch_id,
            created_by=created_by,
            metadata={'payment_method': payment_method, **(metadata or {})}
        )
        
        self.validate_transaction(transaction)
        return self.create_transaction(transaction)