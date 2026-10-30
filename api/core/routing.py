"""Channels routing for the manager web UI (websocket chat)."""
from django.urls import re_path

from core.consumers import ManagerChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/manager/chat/(?P<tg_id>\d+)/$", ManagerChatConsumer.as_asgi()),
]
