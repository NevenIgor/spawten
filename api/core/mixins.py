"""Base model mixins for the application."""
import uuid

from django.db import models

from core.translations import translate_lazy


class UUIDMixin(models.Model):
    """Mixin: UUID primary key instead of numeric id."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=translate_lazy("base.id"),
    )

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """Mixin: bookkeeping fields created / modified."""

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=translate_lazy("base.created"),
    )
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=translate_lazy("base.modified"),
    )

    class Meta:
        abstract = True


class BaseModel(UUIDMixin, TimeStampedMixin):
    """Convenient parent for all business models: uuid + created + modified."""

    class Meta:
        abstract = True
