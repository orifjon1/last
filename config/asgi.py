import os
import config.routing
import config.CustomMiddleware
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddleware
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
        'http': get_asgi_application(),
        'websocket': config.CustomMiddleware.JWTAuthMiddleware(
            AllowedHostsOriginValidator(
                AuthMiddlewareStack(
                                URLRouter(
                                    config.routing.websocket_urlpatterns
                                )
                )
            )
        )
    }
)
