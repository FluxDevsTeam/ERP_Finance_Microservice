from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AssetCategoryViewSet, AssetViewSet, AssetDisposalViewSet

router = DefaultRouter()
router.register('categories', AssetCategoryViewSet, basename='asset-category')
router.register('assets', AssetViewSet, basename='asset')
router.register('disposals', AssetDisposalViewSet, basename='asset-disposal')

urlpatterns = router.urls