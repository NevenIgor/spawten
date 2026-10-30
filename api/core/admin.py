"""Django admin registration.

Все подписи разделов берутся из файла перевода ``core.translations``;
названия статусов выводятся в текущем языке через ``status_display``.
"""
from django.contrib import admin

from core.models import Lead, Status
from core.translations import status_display, translate


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "translated_name", "created", "modified")
    search_fields = ("name",)

    @admin.display(description=translate("status_name"))
    def translated_name(self, obj):
        """Status label in the active language (DB keeps the canonical name)."""
        return status_display(obj.name)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "tg_id",
        "relative_full_name",
        "status",
        "contact_phone",
        "first_contact_date",
        "created",
    )
    list_filter = ("status", "first_contact_date")
    search_fields = ("full_name", "relative_full_name", "contact_phone", "tg_id")
    readonly_fields = ("id", "created", "modified")
    fieldsets = (
        (None, {"fields": ("tg_id", "status", "first_contact_date", "note")}),
        (translate("admin.section_lead"), {
            "fields": ("full_name", "workplace", "contact_phone"),
        }),
        (
            translate("admin.section_relative"),
            {
                "fields": (
                    "relative_full_name",
                    "relative_birth_date",
                    "relative_workplace",
                    "relative_location",
                    "relationship",
                    "photo",
                )
            },
        ),
        (translate("admin.section_additional"), {
            "fields": ("additional_info", "additional_media"),
        }),
        (translate("admin.section_meta"), {"fields": ("id", "created", "modified")}),
    )
