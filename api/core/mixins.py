"""Базовые миксины для моделей приложения."""
import uuid

from django.db import models


class UUIDMixin(models.Model):
    """Миксин: pk в виде UUID вместо числового id."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="UUID",
    )

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """Миксин: служебные поля created / modified."""

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Изменено",
    )

    class Meta:
        abstract = True


class BaseModel(UUIDMixin, TimeStampedMixin):
    """Удобный родитель для всех бизнес-моделей: uuid + created + modified."""

    class Meta:
        abstract = True
