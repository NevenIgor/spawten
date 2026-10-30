from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", lambda request: JsonResponse({"status": "ok"}), name="healthz"),
    path("", core_views.inbox, name="core:inbox"),
    path("chat/<uuid:pk>/", core_views.chat_room, name="core:chat"),
    path("api/", include("core.urls")),
]
