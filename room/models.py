import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()


class Content(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=200)
	url = models.URLField()
	thumbnail = models.URLField(blank=True, null=True, help_text="Optional image URL for the content")
	duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration in seconds")

	def __str__(self):
		return self.title


class Room(models.Model):
	CATEGORY_MOVIE = 'mo'
	CATEGORY_MUSIC = 'mu'
	CATEGORY_GAME = 'ga'
	CATEGORY_CHOICES = [
		(CATEGORY_MOVIE, 'Movie'),
		(CATEGORY_MUSIC, 'Music'),
		(CATEGORY_GAME, 'Game'),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	host = models.ForeignKey(User, related_name='room', on_delete=models.CASCADE)
	category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=CATEGORY_MOVIE)
	max_participants = models.PositiveIntegerField(default=10)
	current_content = models.ForeignKey(Content, related_name='rooms', on_delete=models.SET_NULL, null=True, blank=True)

	is_public = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def add_participant(self, user):
		if self.participants.aggregate(num=Count('id'))['num'] < self.max_participants:
			participant = Participant(room=self, user=user)
			participant.save()
			return participant
		else:
			raise ValueError("Room is full")

	def remove_participant(self, user):
		try:
			participant = self.participants.get(user=user)
			participant.delete()
			return True
		except Participant.DoesNotExist:
			return False

	def total_participants(self):
		return self.participants.count() + 1

	def get_content(self):
		return self.current_content if self.current_content else None

	@property
	def is_full(self):
		return self.participants.count() + 1 >= self.max_participants

	def __str__(self):
		return f"{self.name}"


class Participant(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	room = models.ForeignKey(Room, related_name='participants', on_delete=models.CASCADE)
	user = models.ForeignKey(User, related_name='participants', on_delete=models.CASCADE)
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('room', 'user')

	def __str__(self):
		return f"{self.user.full_name}"
