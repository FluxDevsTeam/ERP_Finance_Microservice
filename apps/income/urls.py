from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import IncomeCategoryViewSet, IncomeViewSet

router = DefaultRouter()
router.register('categories', IncomeCategoryViewSet, basename='income-category')
router.register('entries', IncomeViewSet, basename='income')

urlpatterns = router.urls
