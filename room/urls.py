from django.urls import path
from .views import RoomViewSet, DirectRoomJoinView, ExitRoomView, DestroyRoomView, UpdateRoomContentVIew, RoomStateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', RoomViewSet, basename='room')

urlpatterns = [
	path("direct-join/<uuid:room_id>/", DirectRoomJoinView.as_view(), name='direct-room-join'),
	path("exit/<uuid:room_id>/", ExitRoomView.as_view(), name='exit-room'),
	path("destroy/<uuid:room_id>/", DestroyRoomView.as_view(), name='destroy-room'),
	path("update-content/<uuid:room_id>/", UpdateRoomContentVIew.as_view(), name='update-room-content'),
	path("state/<uuid:room_id>/", RoomStateView.as_view(), name='get-room-state'),
]

urlpatterns += router.urls

