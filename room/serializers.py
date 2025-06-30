from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from .models import Room, Content, State
from django.contrib.auth import get_user_model

User = get_user_model()


class RoomCreateSerializer(ModelSerializer):
	class Meta:
		model = Room
		fields = (
			'id',
			'name',
			'description',
			'category',
			'max_participants',
			'is_public',
		)

	def create(self, validated_data):
		validated_data['host'] = self.context['request'].user
		return super().create(validated_data)


class ContentSerializer(ModelSerializer):
	class Meta:
		model = Content
		fields = [
			'id',
			'title',
			'url',
			'thumbnail',
			'duration',
		]


class RoomListSerializer(ModelSerializer):
	host = SimpleUserSerializer()
	total_participants = serializers.SerializerMethodField()
	content = serializers.SerializerMethodField()

	class Meta:
		model = Room
		fields = (
			'id',
			'name',
			'description',
			'is_full',
			'total_participants',
			'max_participants',
			'content',
			'host',
		)

	def get_total_participants(self, obj):
		return obj.total_participants()

	def get_content(self, obj):
		return ContentSerializer(obj.current_content).data if obj.current_content else None


class UpdateRoomContentSerializer(Serializer):
	video_id = serializers.CharField(required=True)


class SimpleStateSerializer(ModelSerializer):
	class Meta:
		model = State
		fields = ['is_playing', 'current_time']


class RoomStateGetSerializer(ModelSerializer):
	host = SimpleUserSerializer()
	total_participants = serializers.SerializerMethodField()
	content = serializers.SerializerMethodField()
	state = SimpleStateSerializer()

	class Meta:
		model = Room
		fields = (
			'id',
			'name',
			'description',
			'is_full',
			'total_participants',
			'max_participants',
			'content',
			'host',
			'state',
		)

	def get_total_participants(self, obj):
		return obj.total_participants()

	def get_content(self, obj):
		return ContentSerializer(obj.current_content).data if obj.current_content else None
