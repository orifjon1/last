from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.db import close_old_connections


@database_sync_to_async
def get_user(id):
    return get_user_model().objects.get(id=id)


class JWTAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        close_old_connections()

        try:
            token = JWTAuthentication().get_validated_token(scope["query_string"].decode("utf-8"))
        except InvalidToken as e:
            print(f"Invalid token: {e}")
            return None
        except TokenError as e:
            print(f"Token error: {e}")
            return None

        user_id = token["user_id"]
        user = await get_user(user_id)

        if user is None:
            print("User not found")
            return None

        scope['user'] = user

        return await self.inner(scope, receive, send)
