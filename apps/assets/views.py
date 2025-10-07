from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import AssetCategory, Asset, AssetDisposal
from .serializers import AssetCategorySerializer, AssetSerializer, AssetDisposalSerializer
from .permissions import IsAssetOwner


class AssetCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticated, IsAssetOwner]

    def get_queryset(self):
        return AssetCategory.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, IsAssetOwner]

    def get_queryset(self):
        return Asset.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )

    @action(detail=True, methods=['post'])
    def depreciate(self, request, pk=None):
        asset = self.get_object()
        date = request.data.get('date', timezone.now().date().isoformat())
        
        try:
            amount = asset.calculate_depreciation(date)
            if amount > 0:
                asset.record_depreciation(date, amount)
                return Response({
                    'status': 'Depreciation recorded successfully',
                    'amount': amount
                })
            return Response({
                'status': 'No depreciation needed',
                'amount': 0
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AssetDisposalViewSet(viewsets.ModelViewSet):
    serializer_class = AssetDisposalSerializer
    permission_classes = [IsAuthenticated, IsAssetOwner]

    def get_queryset(self):
        return AssetDisposal.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        disposal = serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )
        disposal.record_disposal()

    @action(detail=True, methods=['post'])
    def record_disposal(self, request, pk=None):
        disposal = self.get_object()
        try:
            journal_entry = disposal.record_disposal()
            return Response({
                'status': 'Asset disposal recorded successfully',
                'journal_entry_id': journal_entry.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )