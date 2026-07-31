from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PmlTechSupportProcessingViewSet

router = DefaultRouter()
router.register(r'processing', PmlTechSupportProcessingViewSet, basename='pml-ts-processing')

urlpatterns = [
    path('', include(router.urls)),
]