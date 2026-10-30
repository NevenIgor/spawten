"""Core application models: statuses and leads.

Все пользовательские подписи берутся из файла перевода Django-подсистемы
:mod:`core.translations` (``api/core/translations.py``) через lazy-хелпер
``translate_lazy()``.
"""
from django.db import models

from core.mixins import BaseModel
from core.translations import translate_lazy


class Status(BaseModel):
    """Lead status (e.g. visited, contacted, in progress, client, archived)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=translate_lazy("status.name"),
    )

    class Meta:
        verbose_name = translate_lazy("status")
        verbose_name_plural = translate_lazy("status_plural")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Lead(BaseModel):
    """Lead — информация о потенциальном клиенте и его родственнике."""

    # --- данные родственника ---
    relative_full_name = models.CharField(
        max_length=255,
        verbose_name=translate_lazy("lead.relative_full_name"),
    )
    relative_birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=translate_lazy("lead.relative_birth_date"),
    )
    relative_workplace = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.relative_workplace"),
    )
    relative_location = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.relative_location"),
    )
    photo = models.ImageField(
        upload_to="leads/photos/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=translate_lazy("lead.photo"),
    )
    additional_info = models.TextField(
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.additional_info"),
    )
    additional_media = models.FileField(
        upload_to="leads/additional/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=translate_lazy("lead.additional_media"),
        help_text=translate_lazy("lead.additional_media.help"),
    )
    relationship = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.relationship"),
    )

    # --- данные лида ---
    full_name = models.CharField(
        max_length=255,
        verbose_name=translate_lazy("lead.full_name"),
    )
    tg_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=translate_lazy("lead.tg_id"),
        help_text=translate_lazy("lead.tg_id.help"),
    )
    workplace = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.workplace"),
    )
    contact_phone = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.contact_phone"),
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="leads",
        null=True,
        blank=True,
        verbose_name=translate_lazy("lead.status"),
    )
    first_contact_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=translate_lazy("lead.first_contact_date"),
    )
    note = models.TextField(
        blank=True,
        default="",
        verbose_name=translate_lazy("lead.note"),
    )

    class Meta:
        verbose_name = translate_lazy("lead")
        verbose_name_plural = translate_lazy("lead_plural")
        ordering = ("-created",)

    def __str__(self):
        return self.full_name

    # convenience: translated status label for templates / admin reprs
    def status_display_name(self) -> str:
        from core.translations import status_display

        return status_display(self.status.name if self.status else "")
