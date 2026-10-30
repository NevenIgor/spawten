"""Файл перевода Django-подсистемы (en / ru).

Telegram-бот переводов не использует — его тексты лежат в ``tg_bot/bot/texts.py``.

Здесь собраны все пользовательские строки Django-части проекта:
подписи моделей и полей (Lead, Status), разделы админки, названия
статусов и варианты родства.

Как переводить
--------------
Каждая запись — это ``"ключ": {"en": "...", "ru": "..."}``.
Правьте только значения в секции ``"ru"``; ключи переименовывать нельзя.
Чтобы добавить язык — допишите в каждую запись ещё один код (``"de"`` и т.п.)
или добавьте новый блок со своими ключами в конце словаря.

Активный язык: переменная окружения ``DJANGO_LANGUAGE`` (``en`` | ``ru``,
по умолчанию ``en``) либо вызов :func:`set_language`.

Использование::

    from core.translations import translate

    name = translate("lead.relative_full_name")          # текущий язык
    name = translate("lead.relative_full_name", lang="ru")

Если перевода нет, используется английский, а затем сам ключ — опечатка
никогда не уронит приложение.
"""
import os

DEFAULT_LANG = "en"

# Активный язык: DJANGO_LANGUAGE=en|ru (по умолчанию en)
CURRENT_LANG = os.getenv("DJANGO_LANGUAGE", DEFAULT_LANG).strip().lower()
if CURRENT_LANG not in ("en", "ru"):
    CURRENT_LANG = DEFAULT_LANG


TRANSLATIONS: dict[str, dict[str, str]] = {
    # ================================================================ модели
    # --- Status ---
    "status": {"en": "Status", "ru": "Статус"},
    "status_plural": {"en": "Statuses", "ru": "Статусы"},
    "status.name": {"en": "Name", "ru": "Название"},
    "status_name": {"en": "Translated name", "ru": "Название (перевод)"},

    # --- Lead ---
    "lead": {"en": "Lead", "ru": "Лид"},
    "lead_plural": {"en": "Leads", "ru": "Лиды"},
    # данные родственника
    "lead.relative_full_name": {"en": "Relative full name", "ru": "ФИО родственника"},
    "lead.relative_birth_date": {"en": "Relative birth date", "ru": "Дата рождения родственника"},
    "lead.relative_workplace": {"en": "Relative workplace", "ru": "Место работы родственника"},
    "lead.relative_location": {"en": "Relative location", "ru": "Местоположение родственника"},
    "lead.photo": {"en": "Photo", "ru": "Фотография"},
    "lead.additional_info": {"en": "Additional info", "ru": "Дополнительная информация"},
    "lead.additional_media": {"en": "Additional media", "ru": "Дополнительное медиа"},
    "lead.relationship": {"en": "Relationship", "ru": "Кем приходится"},
    # данные лида
    "lead.full_name": {"en": "Full name", "ru": "ФИО"},
    "lead.tg_id": {"en": "Telegram ID", "ru": "Telegram ID"},
    "lead.workplace": {"en": "Workplace", "ru": "Место работы"},
    "lead.contact_phone": {"en": "Contact phone", "ru": "Контактный телефон"},
    "lead.status": {"en": "Status", "ru": "Статус"},
    "lead.first_contact_date": {"en": "First contact date", "ru": "Дата первого контакта"},
    "lead.note": {"en": "Note", "ru": "Примечание"},
    # служебные поля (TimeStampedMixin / UUIDMixin)
    "base.id": {"en": "UUID", "ru": "UUID"},
    "base.created": {"en": "Created", "ru": "Создано"},
    "base.modified": {"en": "Modified", "ru": "Изменено"},

    # ============================================================ help_texts
    "lead.tg_id.help": {
        "en": "Telegram user numeric ID.",
        "ru": "Числовой идентификатор пользователя Telegram.",
    },
    "lead.additional_media.help": {
        "en": "Image / video / video note uploaded via the bot.",
        "ru": "Фото / видео / видеосообщение, загруженные через бота.",
    },

    # ============================================================== админка
    "admin.site_header": {"en": "Administration", "ru": "Администрирование"},
    "admin.healthz_status": {"en": "ok", "ru": "ок"},
    "admin.site_title": {"en": "Site administration", "ru": "Администрирование сайта"},
    "admin.index_title": {"en": "Site administration", "ru": "Администрирование сайта"},
    "admin.section_lead": {"en": "Lead data", "ru": "Данные лида"},
    "admin.section_relative": {"en": "Relative", "ru": "Родственник"},
    "admin.section_additional": {"en": "Additional", "ru": "Дополнительно"},
    "admin.section_meta": {"en": "Meta", "ru": "Служебное"},

    # ====================================================== статусы и родство
    "status_name.visitor": {"en": "Visitor", "ru": "Посетитель"},
    "status_name.order": {"en": "Order", "ru": "Заказ"},
    "status_name.contacted": {"en": "Contacted", "ru": "Связались"},
    "status_name.in_progress": {"en": "In progress", "ru": "В работе"},
    "status_name.client": {"en": "Client", "ru": "Клиент"},
    "status_name.archived": {"en": "Archived", "ru": "Архив"},

    "relationship.wife": {"en": "Wife", "ru": "Жена"},
    "relationship.mother": {"en": "Mother", "ru": "Мать"},
    "relationship.father": {"en": "Father", "ru": "Отец"},
    "relationship.sister": {"en": "Sister", "ru": "Сестра"},
    "relationship.son": {"en": "Son", "ru": "Сын"},
    "relationship.daughter": {"en": "Daughter", "ru": "Дочь"},
}


# canonical DB status names -> translation keys
_STATUS_KEYS = {
    "visitor": "status_name.visitor",
    "order": "status_name.order",
    "contacted": "status_name.contacted",
    "in progress": "status_name.in_progress",
    "client": "status_name.client",
    "archived": "status_name.archived",
}


def status_display(name: str, lang: str | None = None) -> str:
    """Return the translated label for a canonical status name."""
    key = _STATUS_KEYS.get((name or "").strip().lower())
    return translate(key, lang) if key else (name or "")


def set_language(lang: str) -> None:
    """Переключить активный язык ('en' или 'ru')."""
    global CURRENT_LANG
    lang = (lang or DEFAULT_LANG).strip().lower()
    if lang in ("en", "ru"):
        CURRENT_LANG = lang


def get_language() -> str:
    return CURRENT_LANG


def translate(key: str, lang: str | None = None) -> str:
    """Вернуть строку для ``key`` на языке ``lang`` (по умолчанию — текущий).

    Fallback: английский -> сам ключ, поэтому отсутствующий перевод не может
    ничего сломать.
    """
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    chosen = (lang or CURRENT_LANG).lower()
    return entry.get(chosen) or entry.get(DEFAULT_LANG) or key


def translate_lazy(key: str):
    """Lazy-вариант :func:`translate` для ``verbose_name`` / ``help_text``.

    Возвращает объект, который вычисляется при каждом обращении и всегда
    использует актуальный язык, даже если он изменился после импорта модуля::

        name = models.CharField(max_length=100,
                                verbose_name=translate_lazy("status.name"))
    """
    from django.utils.translation import gettext_lazy

    return gettext_lazy(translate(key))
