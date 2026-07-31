from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftEnlargementViewSet, EnlargeMineralRightViewSet

router = DefaultRouter()
router.register(r'drafts', DraftEnlargementViewSet, basename='enlargement-draft')
router.register(r'enlargements', EnlargeMineralRightViewSet, basename='enlargement')

urlpatterns = [
    path('', include(router.urls)),
]