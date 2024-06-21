from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentsViewSet

router = DefaultRouter()
router.register(r'', CommentsViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
]