from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from room.models import Room
from room.serializers import RoomListSerializer


@receiver(pre_save, sender=Room)
def broadcast_current_content_change(sender, instance: Room,  **kwargs):
	if not instance.pk:
		return

	try:
		old_instance = Room.objects.get(pk=instance.pk)
	except Room.DoesNotExist:
		return

	old_content_id = old_instance.current_content.id if old_instance.current_content else None
	new_content_id = instance.current_content.id if instance.current_content else None

	if old_content_id != new_content_id:
		channel_layer = get_channel_layer()
		room_group_name = f"room_{instance.pk}"

		payload = {
			'type': 'content_change',
			'data': {
				'id': str(new_content_id) if new_content_id else None,
				'title': instance.current_content.title if instance.current_content else None,
				'url': instance.current_content.url if instance.current_content else None,
				'thumbnail': instance.current_content.thumbnail if instance.current_content else None,
				'duration': instance.current_content.duration if instance.current_content else None,
			}
		}

		async_to_sync(channel_layer.group_send)(
			room_group_name,
			payload
		)


@receiver(post_save, sender=Room)
def broadcast_room_change(sender, instance, created, **kwargs):
	if not instance.is_active:
		return

	event_type = "room_created" if created else "room_updated"

	serializer = RoomListSerializer(instance)
	async_to_sync(get_channel_layer().group_send)(
		"home",
		{
			"type": "send_home_update",
			"event": event_type,
			"room": serializer.data
		}
	)


@receiver(pre_delete, sender=Room)
def broadcast_room_deletion(sender, instance, **kwargs):
	serializer = RoomListSerializer(instance)
	async_to_sync(get_channel_layer().group_send)(
		"home",
		{
			"type": "send_home_update",
			"event": "room_deleted",
			"room": serializer.data
		}
	)
