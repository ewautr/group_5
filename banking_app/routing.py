from django.urls import re_path

from . import consumers

# as_asgi() similar to Django’s as_view()
websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<room_name>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]