from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftSuspensionViewSet, SuspendMineralRightViewSet

router = DefaultRouter()
router.register(r'drafts', DraftSuspensionViewSet, basename='suspension-draft')
router.register(r'suspensions', SuspendMineralRightViewSet, basename='suspension')

urlpatterns = [
    path('', include(router.urls)),
]