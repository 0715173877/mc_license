from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftRenewalViewSet, RenewalViewSet

router = DefaultRouter()
router.register(r'drafts', DraftRenewalViewSet, basename='renewal-draft')
router.register(r'renewals', RenewalViewSet, basename='renewal')

urlpatterns = [
    path('', include(router.urls)),
]