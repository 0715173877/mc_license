from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftComplexShapeViewSet, ComplexShapeDocumentViewSet

router = DefaultRouter()
router.register(r'drafts', DraftComplexShapeViewSet, basename='complex-shape-draft')
router.register(r'documents', ComplexShapeDocumentViewSet, basename='complex-shape')

urlpatterns = [
    path('', include(router.urls)),
]