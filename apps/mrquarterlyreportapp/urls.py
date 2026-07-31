from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftQuarterlyReportViewSet, QuarterlyReportViewSet

router = DefaultRouter()
router.register(r'drafts', DraftQuarterlyReportViewSet, basename='quarterly-report-draft')
router.register(r'reports', QuarterlyReportViewSet, basename='quarterly-report')

urlpatterns = [
    path('', include(router.urls)),
]