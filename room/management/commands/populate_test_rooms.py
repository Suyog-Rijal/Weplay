import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from room.models import Room, Content

User = get_user_model()

YOUTUBE_CONTENT = [
	{
		"title": "Interstellar - Official Trailer",
		"url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
		"image_url": "https://img.youtube.com/vi/zSWdZVtXT7E/hqdefault.jpg",
		"duration": 169  # seconds
	},
	{
		"title": "The Batman Theme",
		"url": "https://www.youtube.com/watch?v=HcZ4FPkzFys",
		"image_url": "https://img.youtube.com/vi/HcZ4FPkzFys/hqdefault.jpg",
		"duration": 247
	},
	{
		"title": "Elden Ring Gameplay Preview",
		"url": "https://www.youtube.com/watch?v=E3Huy2cdih0",
		"image_url": "https://img.youtube.com/vi/E3Huy2cdih0/hqdefault.jpg",
		"duration": 1053
	},
	{
		"title": "Inception Soundtrack - Time",
		"url": "https://www.youtube.com/watch?v=RxabLA7UQ9k",
		"image_url": "https://img.youtube.com/vi/RxabLA7UQ9k/hqdefault.jpg",
		"duration": 284
	},
	{
		"title": "Avengers Endgame Trailer",
		"url": "https://www.youtube.com/watch?v=TcMBFSGVi1c",
		"image_url": "https://img.youtube.com/vi/TcMBFSGVi1c/hqdefault.jpg",
		"duration": 152
	},
	{
		"title": "Lo-fi Chill Beats",
		"url": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
		"image_url": "https://img.youtube.com/vi/jfKfPfyJRdk/hqdefault.jpg",
		"duration": 3600
	},
	{
		"title": "Cyberpunk 2077 Trailer",
		"url": "https://www.youtube.com/watch?v=8X2kIfS6fb8",
		"image_url": "https://img.youtube.com/vi/8X2kIfS6fb8/hqdefault.jpg",
		"duration": 268
	},
]

CATEGORIES = ['mo', 'mu', 'ga']

ROOM_NAMES = [
	"Galaxy Watchers", "CineLounge", "LoFi Central", "The Game Hub",
	"Retro Rewind", "Marvel Fans", "Inceptionists", "The Beat Cave",
	"Virtual Theater", "LoFi Hideout", "Gamers Unite", "Epic Watchers",
	"SoundScape", "Movie Junkies", "RPG Realm", "Super Streamers",
	"Chill Vibes", "Future Flicks", "Music Den", "The Watchzone"
]

class Command(BaseCommand):
	help = "Populate dummy Rooms and Content"

	def handle(self, *args, **kwargs):
		users = list(User.objects.all())
		if not users:
			self.stdout.write(self.style.ERROR("No users found in the database. Please create at least one user."))
			return

		for name in ROOM_NAMES:
			content_data = random.choice(YOUTUBE_CONTENT)
			content, _ = Content.objects.get_or_create(
				title=content_data['title'],
				url=content_data['url'],
				defaults={
					"image_url": content_data['image_url'],
					"duration": content_data['duration'],
				}
			)

			room = Room.objects.create(
				name=name,
				description=f"A room for watching {content.title}",
				host=random.choice(users),
				category=random.choice(CATEGORIES),
				max_participants=random.randint(5, 20),
				current_content=content,
				is_public=True,
				is_active=True
			)

			self.stdout.write(self.style.SUCCESS(f"Created Room: {room.name}"))
