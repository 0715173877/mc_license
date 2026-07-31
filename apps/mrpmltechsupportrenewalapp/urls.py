from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftPmlTechSupportRenewalViewSet, PmlTechnicalSupportRenewalViewSet

router = DefaultRouter()
router.register(r'drafts', DraftPmlTechSupportRenewalViewSet, basename='pml-tech-renewal-draft')
router.register(r'renewals', PmlTechnicalSupportRenewalViewSet, basename='pml-tech-renewal')

urlpatterns = [
    path('', include(router.urls)),
]