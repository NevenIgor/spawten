from django.contrib import admin

from core.models import Lead, Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")
    search_fields = ("name",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "relative_full_name",
        "status",
        "contact_phone",
        "first_contact_date",
        "created",
    )
    list_filter = ("status", "first_contact_date")
    search_fields = ("full_name", "relative_full_name", "contact_phone")
    readonly_fields = ("id", "created", "modified")
