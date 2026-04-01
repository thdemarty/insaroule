# chat/middleware.py
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_from_jwt(token_key):
    try:
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import AccessToken

        User = get_user_model()
        access_token = AccessToken(token_key)
        return User.objects.get(pk=access_token["user_id"])

    except Exception as e:
        print("JWTAuthMiddleware error:", e)
        return None


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", {}))
        auth_header = headers.get(b"authorization", b"").decode().split()

        if len(auth_header) == 2 and auth_header[0].lower() == "bearer":
            jwt_user = await get_user_from_jwt(auth_header[1])

            if jwt_user:
                scope["user"] = jwt_user
        return await self.inner(scope, receive, send)
