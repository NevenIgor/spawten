"""Core application models: lead statuses, leads, telegram profiles and chat.

Все пользовательские подписи берутся из файла перевода Django-подсистемы
:mod:`core.translations` (``api/core/translations.py``) через lazy-хелпер
``translate_lazy()``.

Канонические статусы лида (используются и ботом, и веб-интерфейсом менеджера):

* ``visitor`` — просто зашёл в бота          -> бледно-жёлтая карточка
* ``order``   — заполнил заявку              -> зелёная карточка
* ``work``    — взят менеджером в работу     -> синяя карточка
* ``lead``    — квалифицированный лид        -> красная карточка
"""
from django.db import models

from core.mixins import BaseModel
from core.translations import translate_lazy


class LeadStatus(BaseModel):
    """Статус лида: каноническое имя + цвет карточки в интерфейсе менеджера."""

    class Color(models.TextChoices):
        YELLOW = "yellow", translate_lazy("color.yellow")
        GREEN = "green", translate_lazy("color.green")
        BLUE = "blue", translate_lazy("color.blue")
        RED = "red", translate_lazy("color.red")
        GRAY = "gray", translate_lazy("color.gray")

    #: canonical names used by the bot / manager UI (card colors per spec)
    CANONICAL: dict[str, tuple[int, str]] = {
        "visitor": (1, Color.YELLOW),
        "order": (2, Color.GREEN),
        "work": (3, Color.BLUE),
        "lead": (4, Color.RED),
    }

    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name=translate_lazy("status.name"),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=translate_lazy("status.order"),
    )
    color = models.CharField(
        max_length=16,
        choices=Color.choices,
        default=Color.GRAY,
        verbose_name=translate_lazy("status.color"),
    )

    class Meta:
        verbose_name = translate_lazy("status")
        verbose_name_plural = translate_lazy("status_plural")
        ordering = ("order", "name")

    def __str__(self):
        return self.name

    @classmethod
    def ensure_canonical(cls) -> list["LeadStatus"]:
        """Create/refresh the four canonical statuses (idempotent)."""
        result = []
        for name, (order, color) in cls.CANONICAL.items():
            obj, _ = cls.objects.update_or_create(name=name, defaults={"order": order, "color": color})
            result.append(obj)
        return result


class Lead(BaseModel):
    """Lead — информация о потенциальном клиенте и его родственнике."""

    # --- данные родственника ---
    relative_full_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
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
        blank=True,
        default="",
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
        LeadStatus,
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
        return self.full_name or (f"tg:{self.tg_id}" if self.tg_id else str(self.pk))

    # convenience: translated status label for templates / admin reprs
    def status_display_name(self) -> str:
        from core.translations import status_display

        return status_display(self.status.name if self.status else "")

    @property
    def status_color(self) -> str:
        """Card color key for the manager UI (yellow/green/blue/red/gray)."""
        return self.status.color if self.status else LeadStatus.Color.GRAY


class TelegramProfile(BaseModel):
    """Данные пользователя Telegram, полученные по его tg_id.

    Часть полей вычисляется эвристически (tg_id в Telegram монотонно растёт со
    временем регистрации), часть приходит из бота при общении с пользователем.
    """

    tg_id = models.BigIntegerField(
        unique=True,
        verbose_name=translate_lazy("tgsnapshot.tg_id"),
        help_text=translate_lazy("tgsnapshot.tg_id.help"),
    )
    username = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.username"),
    )
    first_name = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.first_name"),
    )
    last_name = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.last_name"),
    )
    language_code = models.CharField(
        max_length=16,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.language_code"),
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name=translate_lazy("tgsnapshot.is_premium"),
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.phone_number"),
        help_text=translate_lazy("tgsnapshot.phone_number.help"),
    )
    registered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=translate_lazy("tgsnapshot.registered_at"),
        help_text=translate_lazy("tgsnapshot.registered_at.help"),
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.location"),
        help_text=translate_lazy("tgsnapshot.location.help"),
    )
    source = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=translate_lazy("tgsnapshot.source"),
        help_text=translate_lazy("tgsnapshot.source.help"),
    )

    class Meta:
        verbose_name = translate_lazy("tgsnapshot")
        verbose_name_plural = translate_lazy("tgsnapshot_plural")
        ordering = ("-created",)

    def __str__(self):
        return f"@{self.username}" if self.username else str(self.tg_id)

    @staticmethod
    def estimated_registration(tg_id: int):
        """Best-effort registration date heuristic based on the id value.

        Early ids are sequential since 2013-03-20; large modern ids are
        unix-timestamp-like (Date.from_unix). Returns None when unknown.
        """
        from datetime import datetime, timedelta, timezone

        if not tg_id:
            return None
        if tg_id < 10 ** 9:  # legacy sequential ids
            base = datetime(2013, 3, 20, tzinfo=timezone.utc)
            return base + timedelta(seconds=tg_id * 1_000_000 / 70_000_000)
        if 1_000_000_000 <= tg_id < 4_000_000_000:  # timestamp-like ids
            return datetime.fromtimestamp(tg_id, tz=timezone.utc)
        return None


class ChatMessage(BaseModel):
    """Сообщение чата «менеджер <-> пользователь» (через бота)."""

    class Direction(models.TextChoices):
        INCOMING = "incoming", translate_lazy("chat.direction_in")
        OUTGOING = "outgoing", translate_lazy("chat.direction_out")

    tg_id = models.BigIntegerField(db_index=True, verbose_name=translate_lazy("chat.tg_id"))
    direction = models.CharField(
        max_length=10,
        choices=Direction.choices,
        verbose_name=translate_lazy("chat.direction"),
    )
    text = models.TextField(verbose_name=translate_lazy("chat.text"))
    attachment_kind = models.CharField(max_length=32, blank=True, default="",
                                       verbose_name=translate_lazy("chat.attachment_kind"))
    attachment_url = models.CharField(max_length=512, blank=True, default="",
                                      verbose_name=translate_lazy("chat.attachment_url"))
    tg_message_id = models.BigIntegerField(null=True, blank=True,
                                           verbose_name=translate_lazy("chat.tg_message_id"))
    sent_by = models.CharField(max_length=150, blank=True, default="",
                               verbose_name=translate_lazy("chat.sent_by"))

    class Meta:
        verbose_name = translate_lazy("chat")
        verbose_name_plural = translate_lazy("chat_plural")
        ordering = ("created",)
        indexes = [models.Index(fields=["tg_id", "created"], name="core_chatm_tg_id_created_idx")]

    def __str__(self):
        return f"[{self.direction}] {self.text[:40]}"
