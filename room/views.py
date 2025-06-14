from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from .models import Room
from .serializers import RoomCreateSerializer, RoomListSerializer


class RoomViewSet(ModelViewSet):
	permission_classes = [IsAuthenticated]
	http_method_names = ['get', 'post']
	serializer_class = RoomListSerializer
	queryset = Room.objects.filter(is_active=True, is_public=True).order_by('-created_at')

	def get_serializer_class(self):
		if self.action == 'create':
			return RoomCreateSerializer
		if self.action == 'list':
			return RoomListSerializer
		return super().get_serializer_class()

	def create(self, *arge, **kwargs):
		print(self.request.data)
		return super().create(*arge, **kwargs)