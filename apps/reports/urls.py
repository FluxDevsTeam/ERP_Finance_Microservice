from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReportTemplateViewSet, GeneratedReportViewSet

router = DefaultRouter()
router.register('templates', ReportTemplateViewSet, basename='report-template')
router.register('reports', GeneratedReportViewSet, basename='generated-report')

urlpatterns = router.urls