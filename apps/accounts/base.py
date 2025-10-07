from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional, Union
from django.db import transaction
from apps.accounts.models import Account, AccountTransaction
from apps.journal.models import JournalEntry, JournalLine


class FinancialTransactionRequest:
    def __init__(
        self,
        date: str,
        description: str,
        amount: Decimal,
        reference: str,
        source_module: str,
        tenant_id: str,
        branch_id: str,
        created_by: str,
        metadata: Optional[Dict] = None
    ):
        self.date = date
        self.description = description
        self.amount = amount
        self.reference = reference
        self.source_module = source_module
        self.tenant_id = tenant_id
        self.branch_id = branch_id
        self.created_by = created_by
        self.metadata = metadata or {}


class BaseFinancialIntegration(ABC):
    """Base class for financial integrations with other modules"""

    def __init__(self, tenant_id: str, branch_id: str):
        self.tenant_id = tenant_id
        self.branch_id = branch_id

    @abstractmethod
    def get_debit_account(self, transaction: FinancialTransactionRequest) -> Account:
        """Return the account to be debited"""
        pass

    @abstractmethod
    def get_credit_account(self, transaction: FinancialTransactionRequest) -> Account:
        """Return the account to be credited"""
        pass

    @transaction.atomic
    def create_transaction(self, transaction: FinancialTransactionRequest) -> JournalEntry:
        """Create a journal entry for the transaction"""
        # Validate accounts
        debit_account = self.get_debit_account(transaction)
        credit_account = self.get_credit_account(transaction)

        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            date=transaction.date,
            reference=f"{transaction.source_module}-{transaction.reference}",
            description=transaction.description,
            tenant=self.tenant_id,
            branch=self.branch_id,
            created_by=transaction.created_by
        )

        # Create debit line
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=debit_account,
            type='debit',
            amount=transaction.amount,
            description=transaction.description,
            tenant=self.tenant_id,
            branch=self.branch_id
        )

        # Create credit line
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account=credit_account,
            type='credit',
            amount=transaction.amount,
            description=transaction.description,
            tenant=self.tenant_id,
            branch=self.branch_id
        )

        # Post the journal entry
        journal_entry.post()

        return journal_entry

    def validate_transaction(self, transaction: FinancialTransactionRequest) -> bool:
        """Validate transaction details before processing"""
        if transaction.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        if not all([transaction.date, transaction.description, transaction.reference]):
            raise ValueError("Missing required transaction details")
        
        return True
