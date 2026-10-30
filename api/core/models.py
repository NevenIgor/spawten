"""Core application models: statuses, leads and chat messages."""
from django.db import models

from core.mixins import BaseModel


class Status(BaseModel):
    """Lead status (e.g. visited, contacted, in progress, client, archived)."""

    VISITOR = "visitor"
    ORDER = "order"

    NEW = "new"
    IN_PROGRESS = "in_progress"
    ANSWERED = "answered"
    CLOSED = "closed"
    STATUS_CHOICES = [
        (NEW, "New"),
        (IN_PROGRESS, "In progress"),
        (ANSWERED, "Answered"),
        (CLOSED, "Closed"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )
    order_status = models.BooleanField(
        default=False,
        verbose_name="Is order status",
        help_text="Leads with this status count as submitted orders.",
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


class ChatMessage(BaseModel):
    """A single message exchanged between the Telegram user and the web UI.

    The bot saves incoming messages here (direction "incoming") and publishes
    them to Redis; the web interface posts operator replies (direction
    "outgoing") and publishes them to Redis; the bot listens for outgoing
    messages and delivers them to Telegram.
    """

    DIRECTION_INCOMING = "incoming"
    DIRECTION_OUTGOING = "outgoing"
    DIRECTION_CHOICES = [
        (DIRECTION_INCOMING, "Incoming (from Telegram user)"),
        (DIRECTION_OUTGOING, "Outgoing (to Telegram user)"),
    ]

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        null=True,
        blank=True,
        verbose_name="Lead",
    )
    tg_id = models.BigIntegerField(
        db_index=True,
        verbose_name="Telegram ID",
        help_text="Telegram user numeric ID this message belongs to.",
    )
    direction = models.CharField(
        max_length=8,
        choices=DIRECTION_CHOICES,
        verbose_name="Direction",
    )
    text = models.TextField(
        blank=True,
        default="",
        verbose_name="Text",
    )
    media_path = models.CharField(
        max_length=512,
        blank=True,
        default="",
        verbose_name="Media path",
        help_text="Path relative to the media root (image/video/document file).",
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Read",
    )

    class Meta:
        verbose_name = "Chat message"
        verbose_name_plural = "Chat messages"
        ordering = ("created",)

    def __str__(self):
        preview = (self.text or self.media_path or "")[:60]
        return f"[{self.direction}] {self.tg_id}: {preview}"
