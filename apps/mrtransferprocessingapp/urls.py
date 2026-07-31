from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransferProcessingViewSet

router = DefaultRouter()
router.register(r'processing', TransferProcessingViewSet, basename='transfer-processing')

urlpatterns = [
    path('', include(router.urls)),
]