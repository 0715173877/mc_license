from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftPmlTechSupportViewSet, PmlTechnicalSupportViewSet

router = DefaultRouter()
router.register(r'drafts', DraftPmlTechSupportViewSet, basename='pml-tech-draft')
router.register(r'pml-tech-supports', PmlTechnicalSupportViewSet, basename='pml-tech-support')

urlpatterns = [
    path('', include(router.urls)),
]