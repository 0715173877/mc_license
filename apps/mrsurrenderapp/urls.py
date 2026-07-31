from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DraftSurrenderViewSet, SurrenderMineralRightViewSet

router = DefaultRouter()
router.register(r'drafts', DraftSurrenderViewSet, basename='surrender-draft')
router.register(r'surrenders', SurrenderMineralRightViewSet, basename='surrender')

urlpatterns = [
    path('', include(router.urls)),
]