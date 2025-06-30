"""
ASGI config for Weplay project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path
from room.consumers import RoomConsumer, FallBackConsumer, HomeConsumer
from room.middlewares import JwtAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Weplay.settings')

application = ProtocolTypeRouter({
	'http': get_asgi_application(),
	'websocket': JwtAuthMiddleware(
		URLRouter([
			re_path(r'ws/room/(?P<room_id>[0-9a-f-]{36})/$', RoomConsumer.as_asgi()),
			re_path(r'ws/home/$', HomeConsumer.as_asgi()),
			re_path(r'^.*$', FallBackConsumer.as_asgi())
		])
	),
})