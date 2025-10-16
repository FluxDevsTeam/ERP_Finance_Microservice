from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, BalanceSwitchViewSet

router = DefaultRouter()
router.register('accounts', AccountViewSet, basename='account')
router.register('balance-switches', BalanceSwitchViewSet, basename='balance-switch')

urlpatterns = router.urls
