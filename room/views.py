from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from youtube.views import fetch_youtube_video_details
from .models import Room, Content
from rest_framework.response import Response
from .serializers import RoomCreateSerializer, RoomListSerializer, UpdateRoomContentSerializer, RoomStateGetSerializer


@extend_schema_view(
	list=extend_schema(tags=["Room"], summary="Get all Public Rooms", description="Returns all active, public rooms."),
	create=extend_schema(tags=["Room"], summary="Create a New Room", description="Creates a new room as host."),
	retrieve=extend_schema(tags=["Room"], summary="Get Specific Room Details",
	                       description="Returns details of a specific room."),
)
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


class DirectRoomJoinView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Room"], summary="Direct Room join",
	               description="Allows a user to join an existing public room directly.")
	def post(self, request, room_id=None):
		user = request.user

		if not room_id:
			return Response(
				{"detail": "Room ID is required."},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			room = Room.objects.filter(id=room_id, is_active=True, is_public=True).first()
			if not room:
				return Response(
					{"detail": "Room not found."},
					status=status.HTTP_404_NOT_FOUND
				)

			if room.host_id == user.id:
				return Response({
					"is_host": True,
					"room_id": room.id
				}, status=status.HTTP_200_OK)

			if room.is_full:
				return Response(
					{"detail": "Room is full."},
					status=status.HTTP_400_BAD_REQUEST
				)

			room.add_participant(user)

			return Response({
				"is_host": False,
				"room_id": room.id
			}, status=status.HTTP_200_OK)
		except Exception as e:
			print(f"Unexpected error: {e}")
			return Response(
				{"detail": "An unexpected error occurred."},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class ExitRoomView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Room"], summary="Exit Room",
	               description="Allows a user to exit a room they are currently in.")
	def post(self, request, room_id=None):

		user = request.user

		if not room_id:
			return Response(
				{"detail": "Room ID is required."},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			room = Room.objects.filter(id=room_id, is_active=True).first()
			if not room:
				return Response(
					{"detail": "Room not found."},
					status=status.HTTP_404_NOT_FOUND
				)

			if room.host_id == user.id:
				return Response({"detail": "Successfully exited the room."}, status=status.HTTP_200_OK)

			if not room.participants.filter(user=user).exists():
				return Response(
					{"detail": "You are not a participant in this room."},
					status=status.HTTP_400_BAD_REQUEST
				)
			room.remove_participant(user)
			return Response(
				{"detail": "Successfully exited the room."},
				status=status.HTTP_200_OK
			)

		except Exception as e:
			print("Unexpected error:", e)
			return Response(
				{"detail": "An unexpected error occurred."},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class DestroyRoomView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Room"], summary="Destroy Room", description="Allows a host to destroy a room they created.")
	def post(self, request, room_id=None):

		user = request.user

		if not room_id:
			return Response(
				{"detail": "Room ID is required."},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			room = Room.objects.filter(id=room_id, host=user, is_active=True).first()
			if not room:
				return Response(
					{"detail": "Room not found or you are not the host."},
					status=status.HTTP_404_NOT_FOUND
				)

			room.is_active = False
			room.save()

			return Response(
				{"detail": "Room successfully destroyed."},
				status=status.HTTP_200_OK
			)
		except Exception as e:
			print("Unexpected error:", e)
			return Response(
				{"detail": "An unexpected error occurred."},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class UpdateRoomContentVIew(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Room"], request=UpdateRoomContentSerializer, summary="Update Room Content",
	               description="Allows a host to update the content(Currently playing video) of a room.")
	def post(self, request, room_id=None):
		if not room_id:
			return Response(
				{"detail": "Room ID is required."},
				status=status.HTTP_400_BAD_REQUEST
			)

		video_id = request.data.get('video_id')
		if not video_id:
			return Response(
				{"detail": "Video ID is required."},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			room = Room.objects.filter(id=room_id, host=request.user, is_active=True).first()
			if not room:
				return Response({
					"detail": "Room not found or you are not the host."
				}, status=status.HTTP_404_NOT_FOUND)

			data = fetch_youtube_video_details(video_id)
			if not data:
				return Response(
					{"detail": "Failed to fetch video details."},
					status=status.HTTP_400_BAD_REQUEST
				)

			url = f"https://www.youtube.com/watch?v={video_id}"
			if room.current_content:
				room.current_content.url = url
				room.current_content.title = data.get('title', "Untitled Video")
				room.current_content.thumbnail = data.get('thumbnail', "")
				room.current_content.duration = data.get('length_seconds', 0)
				room.current_content.save()
			else:
				content = Content.objects.create(
					title=data.get('title', "Untitled Video"),
					url=url,
					thumbnail=data.get('thumbnail', ""),
					duration=data.get('duration', 0)
				)
				room.current_content = content
			room.save()

			return Response(
				{"detail": "Room content updated successfully."},
				status=status.HTTP_200_OK
			)
		except Exception as e:
			print("Unexpected error:", e)
			return Response(
				{"detail": "An unexpected error occurred."},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class RoomStateView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Room"], summary="Update Room Content", description="Allows a user to get the current state of a room.")
	def get(self, request, room_id=None):
		if not room_id:
			return Response({
				"detail": "Room ID is required."
			}, status=status.HTTP_400_BAD_REQUEST)

		try:
			room = Room.objects.filter(id=room_id, is_active=True).first()
			if not room:
				return Response({
					'detail': "Room not found."
				}, status=status.HTTP_404_NOT_FOUND)

			serializer = RoomStateGetSerializer(room, context={'request': request})
			return Response({
				'room': serializer.data,
			}, status=status.HTTP_200_OK)
		except Exception as e:
			print("Unexpected error:", e)
			return Response({
				"detail": "An unexpected error occurred."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
