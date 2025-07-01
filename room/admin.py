from django.contrib import admin
from django.utils.text import Truncator

from .models import Room, Participant, Content, State


class ParticipantInline(admin.TabularInline):
	model = Participant
	extra = 1
	readonly_fields = ('joined_at',)
	autocomplete_fields = ['user']
	show_change_link = True


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = (
		'name', 'host', 'category', 'current_content_short',
		'max_participants', 'is_public', 'is_active', 'is_full_display'
	)
	list_filter = ('category', 'is_public', 'is_active')
	search_fields = ('name', 'description', 'host__email', 'host__full_name')
	readonly_fields = ('created_at', 'updated_at')
	autocomplete_fields = ['host']
	inlines = [ParticipantInline]

	def is_full_display(self, obj):
		return obj.is_full

	is_full_display.boolean = True
	is_full_display.short_description = 'Is Full?'

	def current_content_short(self, obj):
		return Truncator(obj.current_content).chars(50)

	current_content_short.short_description = 'Current Content'


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	list_display = ('user', 'room', 'joined_at')
	list_filter = ('room__category',)
	search_fields = ('user__email', 'user__full_name', 'room__name')
	autocomplete_fields = ['user', 'room']
	readonly_fields = ('joined_at',)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
	list_display = ('title', 'url', 'duration')
	search_fields = ('title',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
	list_display = ('room', 'current_time', 'is_playing')
