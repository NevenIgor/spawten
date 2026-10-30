from django.contrib import admin

from core.models import ChatMessage, Lead, Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order_status", "created", "modified")
    list_editable = ("order_status",)
    search_fields = ("name",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "direction", "text", "is_read", "created")
    list_filter = ("direction", "is_read")
    search_fields = ("tg_id", "text")
    readonly_fields = ("id", "created", "modified")


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
        ("Lead data", {"fields": ("full_name", "workplace", "contact_phone")}),
        (
            "Relative",
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
        ("Additional", {"fields": ("additional_info", "additional_media")}),
        ("Meta", {"fields": ("id", "created", "modified")}),
    )
