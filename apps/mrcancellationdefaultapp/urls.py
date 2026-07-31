from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftCancellationDefaultViewSet, CancellationSuspensionMineralRightViewSet

router = DefaultRouter()
router.register(r'drafts', DraftCancellationDefaultViewSet, basename='cancellation-default-draft')
router.register(r'cancellations', CancellationSuspensionMineralRightViewSet, basename='cancellation-default')

urlpatterns = [
    path('', include(router.urls)),
]