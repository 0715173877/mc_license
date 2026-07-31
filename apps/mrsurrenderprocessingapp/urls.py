from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurrenderProcessingViewSet

router = DefaultRouter()
router.register(r'processing', SurrenderProcessingViewSet, basename='surrender-processing')

urlpatterns = [
    path('', include(router.urls)),
]