from channels.db import database_sync_to_async


@database_sync_to_async
def get_user(token_key):
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import AccessToken

    try:
        access_token = AccessToken(token_key)
        return get_user_model().objects.get(id=access_token["user_id"])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Custom middleware that takes a JWT token from the query string and authenticates the user.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        headers = dict(scope["headers"])
        if b"authorization" in headers:
            try:
                token_name, token_key = headers[b"authorization"].decode().split()
                if token_name.lower() == "bearer":
                    scope["user"] = await get_user(token_key)
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)
