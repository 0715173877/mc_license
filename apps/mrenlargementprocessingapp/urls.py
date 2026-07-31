from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnlargementProcessingViewSet

router = DefaultRouter()
router.register(r'processing', EnlargementProcessingViewSet, basename='enlargement-processing')

urlpatterns = [
    path('', include(router.urls)),
]