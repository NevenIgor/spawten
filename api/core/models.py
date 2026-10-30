"""Модели приложения core: статусы и лиды."""
from django.db import models

from core.mixins import BaseModel


class Status(BaseModel):
    """Статус лида (например: посетили, обратились, в работе, клиент, архив)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Lead(BaseModel):
    """Лид — информация о потенциальном клиенте и его родственнике."""

    # --- Данные родственника ---
    relative_full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО родственника",
    )
    relative_birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата рождения родственника",
    )
    relative_workplace = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Место работы родственника",
    )
    relative_location = models.DateField(
        null=True,
        blank=True,
        verbose_name="Место нахождения родственника",
        help_text="Поле указано как дата согласно требованиям.",
    )
    photo = models.ImageField(
        upload_to="leads/photos/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Фото",
    )
    additional_info = models.TextField(
        blank=True,
        default="",
        verbose_name="Доп. информация",
    )
    relationship = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Кем приходится",
    )

    # --- Данные лида ---
    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО",
    )
    workplace = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Место работы",
    )
    contact_phone = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="Контактный телефон",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="leads",
        null=True,
        blank=True,
        verbose_name="Статус",
    )
    first_contact_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата первого обращения",
    )
    note = models.TextField(
        blank=True,
        default="",
        verbose_name="Примечание",
    )

    class Meta:
        verbose_name = "Лид"
        verbose_name_plural = "Лиды"
        ordering = ("-created",)

    def __str__(self):
        return self.full_name
