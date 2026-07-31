from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftTransferViewSet, TransferViewSet

router = DefaultRouter()
router.register(r'drafts', DraftTransferViewSet, basename='draft')
router.register(r'transfers', TransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]