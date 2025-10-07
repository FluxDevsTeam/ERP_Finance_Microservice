from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Account, AccountCategory, AccountTransaction
from .serializers import (
    AccountSerializer,
    AccountCategorySerializer,
    AccountTransactionSerializer,
)
from .permissions import IsAccountOwner
from .role_permissions import finance_roles_required, HasFinanceRole


@finance_roles_required('finance_admin', 'finance_manager')
class AccountCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AccountCategorySerializer
    permission_classes = [IsAuthenticated, IsAccountOwner, HasFinanceRole]

    def get_queryset(self):
        return AccountCategory.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return Account.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )


class AccountTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = AccountTransactionSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return AccountTransaction.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )