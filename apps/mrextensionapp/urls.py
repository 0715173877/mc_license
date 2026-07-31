from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftExtensionViewSet, ExtensionToCommenceMiningViewSet

router = DefaultRouter()
router.register(r'drafts', DraftExtensionViewSet, basename='extension-draft')
router.register(r'extensions', ExtensionToCommenceMiningViewSet, basename='extension')

urlpatterns = [
    path('', include(router.urls)),
]