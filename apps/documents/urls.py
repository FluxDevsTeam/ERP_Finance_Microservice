from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, DocumentVersionViewSet, DocumentWorkflowViewSet,
    DocumentAccessViewSet, DocumentCommentViewSet, DocumentAuditViewSet
)

router = DefaultRouter()
router.register('documents', DocumentViewSet)
router.register('versions', DocumentVersionViewSet)
router.register('workflows', DocumentWorkflowViewSet)
router.register('access', DocumentAccessViewSet)
router.register('comments', DocumentCommentViewSet)
router.register('audit', DocumentAuditViewSet)

urlpatterns = [
    path('', include(router.urls)),
]