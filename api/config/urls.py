from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", lambda request: JsonResponse({"status": "ok"}), name="healthz"),
]
