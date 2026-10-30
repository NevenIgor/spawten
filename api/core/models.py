"""Core application models: statuses and leads."""
from django.db import models

from core.mixins import BaseModel


class Status(BaseModel):
    """Lead status (e.g. visited, contacted, in progress, client, archived)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Lead(BaseModel):
    """Lead — information about a potential client and their relative."""

    # --- Relative data ---
    relative_full_name = models.CharField(
        max_length=255,
        verbose_name="Relative full name",
    )
    relative_birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Relative birth date",
    )
    relative_workplace = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Relative workplace",
    )
    relative_location = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Relative location",
    )
    photo = models.ImageField(
        upload_to="leads/photos/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Photo",
    )
    additional_info = models.TextField(
        blank=True,
        default="",
        verbose_name="Additional info",
    )
    additional_media = models.FileField(
        upload_to="leads/additional/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Additional media",
        help_text="Image / video / video note uploaded via the bot.",
    )
    relationship = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Relationship",
    )

    # --- Lead data ---
    full_name = models.CharField(
        max_length=255,
        verbose_name="Full name",
    )
    tg_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram ID",
        help_text="Telegram user numeric ID.",
    )
    workplace = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Workplace",
    )
    contact_phone = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="Contact phone",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="leads",
        null=True,
        blank=True,
        verbose_name="Status",
    )
    first_contact_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="First contact date",
    )
    note = models.TextField(
        blank=True,
        default="",
        verbose_name="Note",
    )

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ("-created",)

    def __str__(self):
        return self.full_name
