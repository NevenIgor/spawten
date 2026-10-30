"""Project URL configuration."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from core import views_manager
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
    # --- менеджерский веб-интерфейс обработки заявок ---
    path("manager/login/", views_manager.login_view, name="manager_login"),
    path("manager/logout/", views_manager.logout_view, name="manager_logout"),
    path("manager/", views_manager.dashboard, name="manager_dashboard"),
    path("manager/stats/", views_manager.stats_view, name="manager_stats"),
    path("manager/api/new-cards/", views_manager.new_cards, name="manager_new_cards"),
    path("manager/lead/<uuid:pk>/", views_manager.lead_detail_view, name="manager_lead_detail"),
    path("manager/lead/<uuid:pk>/status/", views_manager.lead_set_status, name="manager_lead_status"),
]
