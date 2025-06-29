from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
	try:
		return User.objects.get(id=user_id)
	except User.DoesNotExist:
		return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
	async def __call__(self, scope, receive, send):
		query_string = scope.get('query_string', b'').decode()
		query_params = parse_qs(query_string)
		token = query_params.get('token')

		if token:
			token = token[0]
			try:
				payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
				user_id = payload.get('user_id')
				user = await get_user(user_id)
				scope['user'] = user
			except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
				scope['user'] = AnonymousUser()
		else:
			scope['user'] = AnonymousUser()

		return await super().__call__(scope, receive, send)
