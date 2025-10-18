from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from .models import Account, BalanceSwitchLog
from .serializers import AccountSerializer, BalanceSwitchLogSerializer
from datetime import date
from .utils import swagger_helper


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    @swagger_helper("Accounts", "Account")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_helper("Accounts", "Account")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_helper("Accounts", "Account")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_helper("Accounts", "Account")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_helper("Accounts", "Account")
    def destroy(self, request, *args, **kwargs):
        """
        Deletes an account instance.
        """
        return super().destroy(request, *args, **kwargs)

    @swagger_helper("Accounts", "Account")
    def update(self, request, *args, **kwargs):
        """
        Update method is not allowed for accounts.
        """
        return Response({"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_helper("Accounts", "Account")
    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.auth['tenant'],
            branch=self.request.auth['branches'][0],  # Using first branch
            created_by=self.request.user.id
        )

    @swagger_helper("Accounts", "Account")
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.id
        )


class BalanceSwitchViewSet(viewsets.ModelViewSet):
    serializer_class = BalanceSwitchLogSerializer
    queryset = BalanceSwitchLog.objects.all()

    @swagger_helper("Balance Switch Logs", "Balance Switch Log")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_helper("Balance Switch Logs", "Balance Switch Log")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_helper("Balance Switch Logs", "Balance Switch Log")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_helper("Balance Switch Logs", "Balance Switch Log")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_helper("Balance Switch Logs", "Balance Switch Log")
    def perform_create(self, serializer):
        with transaction.atomic():
            from_account = serializer.validated_data['from_account']
            to_account = serializer.validated_data['to_account']
            amount = serializer.validated_data['amount']
            switch_date = serializer.validated_data.get('switch_date', date.today())

            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

            serializer.save()

    def perform_update(self, serializer):
        with transaction.atomic():
            instance = self.get_object()
            from_account = serializer.validated_data.get('from_account', instance.from_account)
            to_account = serializer.validated_data.get('to_account', instance.to_account)
            amount = serializer.validated_data.get('amount', instance.amount)

            # Reverse the original transfer
            instance.from_account.balance += instance.amount
            instance.to_account.balance -= instance.amount
            instance.from_account.save()
            instance.to_account.save()

            # Apply the new transfer
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

            serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.from_account.balance += instance.amount
            instance.to_account.balance -= instance.amount
            instance.from_account.save()
            instance.to_account.save()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)