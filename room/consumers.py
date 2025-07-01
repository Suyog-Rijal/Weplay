import uuid
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from room.models import Room
import json
from datetime import datetime


class RoomConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		user = self.scope.get('user')
		if user is None or user.is_anonymous:
			await self.close(code=4004, reason="Forbidden: Authentication required.")
			return

		room_id_str = self.scope['url_route']['kwargs'].get('room_id')
		try:
			room_id = uuid.UUID(room_id_str)
		except (ValueError, TypeError):
			await self.close(code=4000, reason="Invalid room ID.")
			return

		exists = await self.room_exists(room_id)
		if not exists:
			await self.close(code=4001, reason="Room does not exist.")
			return

		self.user = user
		self.room_id = room_id
		self.room_group_name = f"room_{room_id}"

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)
		await self.accept()

		now = datetime.now()
		hour = now.strftime("%I").lstrip("0") or "0"
		minute = now.strftime("%M")
		ampm = now.strftime("%p")
		formatted_time = f"{hour}:{minute} {ampm}"

		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'system_message',
				'data': {
					'user_id': '0',
					'full_name': 'System',
					'user_profile_picture': "",
					'message': f"{user.full_name} joined the room.",
					'timestamp': formatted_time
		}
			}
		)

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)
		now = datetime.now()
		hour = now.strftime("%I").lstrip("0") or "0"
		minute = now.strftime("%M")
		ampm = now.strftime("%p")
		formatted_time = f"{hour}:{minute} {ampm}"

		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'system_message',
				'data': {
					'user_id': '0',
					'full_name': 'System',
					'user_profile_picture': "",
					'message': f"{self.user.full_name} left the room.",
					'timestamp': formatted_time
				}
			}
		)

	async def receive(self, text_data=None, bytes_data=None):
		try:
			data = json.loads(text_data)
			event_type = data.get('type')
		except Exception as e:
			print(f"Error parsing message: {e}")
			return

		if event_type == 'chat_message':
			await self.handle_chat_message(data)

	async def system_message(self, event):
		await self.send(text_data=json.dumps({
			'type': 'system_message',
			'data': event.get('data', {})
		}))

	async def chat_message(self, event):
		await self.send(text_data=json.dumps({
			'type': 'chat_message',
			'data': event.get('data', {})
		}))

	async def handle_chat_message(self, data):
		message = data.get('message', '').strip()
		if not message:
			return

		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'chat_message',
				'data': {
					'user_id': str(self.user.id),
					'full_name': self.user.full_name,
					'user_profile_picture': self.user.profile_picture or "",
					'message': message
				}
			}
		)

	async def content_change(self, event):
		await self.send(text_data=json.dumps({
			'type': 'content_change',
			'data': event.get('data', {})
		}))

	@database_sync_to_async
	def room_exists(self, room_id):
		return Room.objects.filter(id=room_id).exists()


class HomeConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		user = self.scope.get('user')
		print(f"Connecting user: {user}")
		if user is None or user.is_anonymous:
			await self.close(code=4004, reason="Forbidden: Authentication required.")
			return

		self.user = user
		self.home_group_name = f"home"
		await self.channel_layer.group_add(
			self.home_group_name,
			self.channel_name
		)
		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.home_group_name,
			self.channel_name
		)

	async def send_home_update(self, event):
		await self.send(text_data=json.dumps({
			"type": event["event"],
			"data": event["room"]
		}))


class FallBackConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		print("Here we go")
		await self.close(code=4002, reason="Forbidden.")

	async def disconnect(self, close_code):
		await self.close(code=4003, reason="Forbidden.")
