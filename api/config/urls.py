"""Project URL configuration."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from core.translations import translate

admin.site.site_header = translate("admin.site_header")
admin.site.site_title = translate("admin.site_title")
admin.site.index_title = translate("admin.index_title")


def healthz(request):
    """Health-check endpoint (response payload is translatable)."""
    return JsonResponse({"status": translate("admin.healthz_status")})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
]
