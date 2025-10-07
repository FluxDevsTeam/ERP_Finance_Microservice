from django.urls import path
from .views import (
    AccountCategoryViewSet,
    AccountViewSet,
    AccountTransactionViewSet,
)
from .integration_views import (
    record_purchase,
    record_payroll,
    record_sale,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('categories', AccountCategoryViewSet, basename='account-category')
router.register('accounts', AccountViewSet, basename='account')
router.register('transactions', AccountTransactionViewSet, basename='account-transaction')

urlpatterns = router.urls + [
    # Integration endpoints
    path('integrations/purchase/', record_purchase, name='record-purchase'),
    path('integrations/payroll/', record_payroll, name='record-payroll'),
    path('integrations/sale/', record_sale, name='record-sale'),
]