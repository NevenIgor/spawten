from django.urls import path

from core import api_views

app_name = "core_api"

urlpatterns = [
    path("leads/", api_views.lead_list, name="leads"),
    path("chats/<int:tg_id>/", api_views.chat_detail, name="chat-detail"),
    path("chats/<int:tg_id>/send/", api_views.chat_send, name="chat-send"),
    path("chats/<int:tg_id>/inject/", api_views.chat_inject, name="chat-inject"),
]
