"""
ASGI config for bank project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import banking_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank.settings')

# root routing configuration for Channels
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            banking_app.routing.websocket_urlpatterns
        )
    ),
})