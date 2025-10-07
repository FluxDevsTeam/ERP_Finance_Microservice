from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from .base import FinancialTransactionRequest
from .integrations import (
    ProcurementIntegration,
    HRIntegration,
    SalesIntegration
)
from .permissions import IsAccountOwner


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAccountOwner])
def record_purchase(request):
    """API endpoint to record purchase transactions from Procurement module"""
    try:
        amount = Decimal(request.data.get('amount'))
        reference = request.data.get('reference')
        description = request.data.get('description')
        item_type = request.data.get('item_type', 'inventory')
        metadata = request.data.get('metadata', {})

        integration = ProcurementIntegration(
            tenant_id=request.tenant_id,
            branch_id=request.branch_id
        )

        journal_entry = integration.record_purchase(
            amount=amount,
            reference=reference,
            description=description,
            created_by=request.user.id,
            item_type=item_type,
            metadata=metadata
        )

        return Response({
            'status': 'success',
            'message': 'Purchase recorded successfully',
            'journal_entry_id': journal_entry.id
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAccountOwner])
def record_payroll(request):
    """API endpoint to record payroll transactions from HR module"""
    try:
        amount = Decimal(request.data.get('amount'))
        reference = request.data.get('reference')
        description = request.data.get('description')
        payment_type = request.data.get('payment_type', 'salary')
        metadata = request.data.get('metadata', {})

        integration = HRIntegration(
            tenant_id=request.tenant_id,
            branch_id=request.branch_id
        )

        journal_entry = integration.record_payroll(
            amount=amount,
            reference=reference,
            description=description,
            created_by=request.user.id,
            payment_type=payment_type,
            metadata=metadata
        )

        return Response({
            'status': 'success',
            'message': 'Payroll recorded successfully',
            'journal_entry_id': journal_entry.id
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAccountOwner])
def record_sale(request):
    """API endpoint to record sales transactions from Sales module"""
    try:
        amount = Decimal(request.data.get('amount'))
        reference = request.data.get('reference')
        description = request.data.get('description')
        payment_method = request.data.get('payment_method', 'credit')
        metadata = request.data.get('metadata', {})

        integration = SalesIntegration(
            tenant_id=request.tenant_id,
            branch_id=request.branch_id
        )

        journal_entry = integration.record_sale(
            amount=amount,
            reference=reference,
            description=description,
            created_by=request.user.id,
            payment_method=payment_method,
            metadata=metadata
        )

        return Response({
            'status': 'success',
            'message': 'Sale recorded successfully',
            'journal_entry_id': journal_entry.id
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)