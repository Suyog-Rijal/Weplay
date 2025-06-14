from django.urls import path
from .views import RoomViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', RoomViewSet, basename='room')

urlpatterns = [
]

urlpatterns += router.urls

