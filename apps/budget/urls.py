from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BudgetViewSet, BudgetItemViewSet, BudgetVarianceViewSet

router = DefaultRouter()
router.register('budgets', BudgetViewSet, basename='budget')
router.register('items', BudgetItemViewSet, basename='budget-item')
router.register('variances', BudgetVarianceViewSet, basename='budget-variance')

urlpatterns = router.urls