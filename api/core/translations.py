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
    # --- LeadStatus ---
    "status": {"en": "Status", "ru": "Статус"},
    "status_plural": {"en": "Statuses", "ru": "Статусы"},
    "status.name": {"en": "Name", "ru": "Название"},
    "status.order": {"en": "Order", "ru": "Порядок"},
    "status.color": {"en": "Card color", "ru": "Цвет карточки"},
    "status_name": {"en": "Translated name", "ru": "Название (перевод)"},
    "color.yellow": {"en": "Pale yellow", "ru": "Бледно-жёлтый"},
    "color.green": {"en": "Green", "ru": "Зелёный"},
    "color.blue": {"en": "Blue", "ru": "Синий"},
    "color.red": {"en": "Red", "ru": "Красный"},
    "color.gray": {"en": "Gray", "ru": "Серый"},

    # --- TelegramProfile (данные по tg_id) ---
    "tgsnapshot": {"en": "Telegram profile", "ru": "Профиль Telegram"},
    "tgsnapshot_plural": {"en": "Telegram profiles", "ru": "Профили Telegram"},
    "tgsnapshot.tg_id": {"en": "Telegram ID", "ru": "Telegram ID"},
    "tgsnapshot.tg_id.help": {"en": "Numeric Telegram user ID (chat id).",
                              "ru": "Числовой идентификатор пользователя Telegram (id чата)."},
    "tgsnapshot.username": {"en": "Username", "ru": "Username (имя пользователя)"},
    "tgsnapshot.first_name": {"en": "First name", "ru": "Имя"},
    "tgsnapshot.last_name": {"en": "Last name", "ru": "Фамилия"},
    "tgsnapshot.language_code": {"en": "Language code", "ru": "Код языка"},
    "tgsnapshot.is_premium": {"en": "Telegram Premium", "ru": "Telegram Premium"},
    "tgsnapshot.phone_number": {"en": "Phone bound to the account", "ru": "Телефон, закреплённый за аккаунтом"},
    "tgsnapshot.phone_number.help": {
        "en": "Visible only if the user shared their contact with the bot.",
        "ru": "Виден, только если пользователь поделился контактом с ботом.",
    },
    "tgsnapshot.registered_at": {"en": "Registered in Telegram since", "ru": "Зарегистрирован в Telegram с"},
    "tgsnapshot.registered_at.help": {
        "en": "Known registration date (from the API or estimated from tg_id).",
        "ru": "Известная дата регистрации (из API или оценка по tg_id).",
    },
    "tgsnapshot.location": {"en": "Location", "ru": "Местоположение"},
    "tgsnapshot.location.help": {"en": "Location shared via the bot, if any.",
                                 "ru": "Координаты, отправленные боту (если были)."},
    "tgsnapshot.source": {"en": "Source", "ru": "Источник данных"},
    "tgsnapshot.source.help": {"en": "How this record was obtained (bot /start, GetUser, ...).",
                               "ru": "Как получена запись (бот /start, GetUser и т.п.)."},

    # --- ChatMessage ---
    "chat": {"en": "Chat message", "ru": "Сообщение чата"},
    "chat_plural": {"en": "Chat messages", "ru": "Сообщения чата"},
    "chat.tg_id": {"en": "Telegram ID", "ru": "Telegram ID"},
    "chat.direction": {"en": "Direction", "ru": "Направление"},
    "chat.direction_in": {"en": "Incoming (from user)", "ru": "Входящее (от пользователя)"},
    "chat.direction_out": {"en": "Outgoing (via bot)", "ru": "Исходящее (через бота)"},
    "chat.text": {"en": "Text", "ru": "Текст"},
    "chat.attachment_kind": {"en": "Attachment kind", "ru": "Тип вложения"},
    "chat.attachment_url": {"en": "Attachment URL", "ru": "Ссылка на вложение"},
    "chat.tg_message_id": {"en": "Telegram message ID", "ru": "ID сообщения Telegram"},
    "chat.sent_by": {"en": "Sent by", "ru": "Отправлено (кем)"},

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

    # =================================================== веб-интерфейс менеджера
    "mgr.login_title": {"en": "Manager login", "ru": "Вход для менеджера"},
    "mgr.username": {"en": "Username", "ru": "Имя пользователя"},
    "mgr.password": {"en": "Password", "ru": "Пароль"},
    "mgr.sign_in": {"en": "Sign in", "ru": "Войти"},
    "mgr.logout": {"en": "Logout", "ru": "Выйти"},
    "mgr.login_failed": {"en": "Wrong username or password.", "ru": "Неверное имя пользователя или пароль."},
    "mgr.dashboard_title": {"en": "Leads", "ru": "Лиды"},
    "mgr.search_placeholder": {"en": "Search: name, phone, tg_id…", "ru": "Поиск: ФИО, телефон, tg_id…"},
    "mgr.search_btn": {"en": "Search", "ru": "Найти"},
    "mgr.reset_btn": {"en": "Reset", "ru": "Сброс"},
    "mgr.no_leads": {"en": "No leads yet — cards appear here as users contact the bot.",
                     "ru": "Заявок пока нет — карточки появятся здесь по мере обращения пользователей к боту."},
    "mgr.new_cards": {"en": "New cards", "ru": "Новых карточек"},
    "mgr.card_created": {"en": "Created", "ru": "Создано"},
    "mgr.card_user": {"en": "User", "ru": "Пользователь"},
    "mgr.card_phone": {"en": "Phone", "ru": "Телефон"},
    "mgr.legend": {"en": "Card colors", "ru": "Цвета карточек"},
    "mgr.filter_all": {"en": "All statuses", "ru": "Все статусы"},
    "mgr.lead_details": {"en": "Lead details", "ru": "Карточка лида"},
    "mgr.back_to_list": {"en": "Back to the list", "ru": "К списку"},
    "mgr.section_lead": {"en": "Client", "ru": "Клиент"},
    "mgr.section_relative": {"en": "Relative", "ru": "Родственник"},
    "mgr.section_tg": {"en": "Telegram data (by tg_id)", "ru": "Данные Telegram (по tg_id)"},
    "mgr.section_service": {"en": "Service information", "ru": "Служебная информация"},
    "mgr.change_status": {"en": "Change status", "ru": "Сменить статус"},
    "mgr.save": {"en": "Save", "ru": "Сохранить"},
    "mgr.saved": {"en": "Saved", "ru": "Сохранено"},
    "mgr.chat_title": {"en": "Chat via the bot", "ru": "Чат через бота"},
    "mgr.chat_hint": {"en": "Real-time conversation with this user on behalf of the bot.",
                      "ru": "Переписка с пользователем в реальном времени от лица бота."},
    "mgr.chat_input_placeholder": {"en": "Type a message for the user…", "ru": "Напишите сообщение пользователю…"},
    "mgr.chat_send": {"en": "Send", "ru": "Отправить"},
    "mgr.chat_empty": {"en": "No messages yet.", "ru": "Сообщений пока нет."},
    "mgr.chat_connected": {"en": "Live connection established", "ru": "Установлено live-соединение"},
    "mgr.chat_disconnected": {"en": "Connection lost, reconnecting…", "ru": "Соединение потеряно, переподключение…"},
    "mgr.not_found": {"en": "Lead not found", "ru": "Лид не найден"},
    "mgr.you": {"en": "You", "ru": "Вы"},
    "mgr.bot": {"en": "Bot", "ru": "Бот"},
    "mgr.user": {"en": "User", "ru": "Пользователь"},
    "mgr.tg_link": {"en": "Open in Telegram", "ru": "Открыть в Telegram"},
    "mgr.tg_none": {"en": "not available", "ru": "нет данных"},
    "mgr.tg_estimate_note": {"en": "estimated from tg_id", "ru": "оценка по tg_id"},
    "mgr.not_filled": {"en": "— not filled in —", "ru": "— не заполнено —"},
    "mgr.attachment": {"en": "attachment", "ru": "вложение"},
    "mgr.premium_yes": {"en": "Premium", "ru": "Premium"},
    "mgr.premium_no": {"en": "Free", "ru": "Обычный"},

    # ------------------------------------------- навигация и фильтры дашборда
    "mgr.nav_leads": {"en": "Leads", "ru": "Лиды"},
    "mgr.nav_stats": {"en": "Statistics", "ru": "Статистика"},
    "mgr.filter_status": {"en": "Status", "ru": "Статус"},
    "mgr.filter_date_from": {"en": "Created from", "ru": "Создано с"},
    "mgr.filter_date_to": {"en": "Created to", "ru": "Создано по"},
    "mgr.sort_label": {"en": "Sort by", "ru": "Сортировка"},
    "mgr.sort_new": {"en": "Newest first", "ru": "Сначала новые"},
    "mgr.sort_old": {"en": "Oldest first", "ru": "Сначала старые"},
    "mgr.sort_name": {"en": "Client name", "ru": "По имени клиента"},
    "mgr.sort_rname": {"en": "Relative name", "ru": "По имени родственника"},
    "mgr.sort_status": {"en": "Status", "ru": "По статусу"},
    "mgr.per_page": {"en": "Per page", "ru": "На странице"},
    "mgr.filled_label": {"en": "Application", "ru": "Заявка"},
    "mgr.filled_any": {"en": "Any", "ru": "Любая"},
    "mgr.filled_yes": {"en": "Filled in", "ru": "Заполнена"},
    "mgr.filled_no": {"en": "Not filled in", "ru": "Не заполнена"},
    "mgr.active_filters": {"en": "Active filters", "ru": "Активные фильтры"},
    "mgr.clear_filters": {"en": "Clear filters", "ru": "Сбросить фильтры"},
    "mgr.results_count": {"en": "Found", "ru": "Найдено"},
    "mgr.no_results": {"en": "Nothing found — try to relax the filters.",
                       "ru": "Ничего не найдено — попробуйте ослабить фильтры."},
    "mgr.show_filters": {"en": "Filters", "ru": "Фильтры"},

    # -------------------------------------------------- страница статистики
    "mgr.stats_title": {"en": "Statistics", "ru": "Статистика"},
    "mgr.stats_total": {"en": "Total leads", "ru": "Всего лидов"},
    "mgr.stats_week": {"en": "New this week", "ru": "Новых за неделю"},
    "mgr.stats_month": {"en": "New this month", "ru": "Новых за месяц"},
    "mgr.stats_active": {"en": "In work this week", "ru": "В работе за неделю"},
    "mgr.stats_conversion": {"en": "Conversion visitor → lead", "ru": "Конверсия посетитель → лид"},
    "mgr.stats_chats": {"en": "Chat messages", "ru": "Сообщений в чатах"},
    "mgr.stats_profiles": {"en": "Telegram profiles", "ru": "Профилей Telegram"},
    "mgr.by_status": {"en": "Leads by status", "ru": "Лиды по статусам"},
    "mgr.dynamics": {"en": "Dynamics over the last 14 days", "ru": "Динамика за 14 дней"},
    "mgr.conversion_funnel": {"en": "Conversion funnel", "ru": "Воронка конверсии"},
    "mgr.top_managers": {"en": "Top managers (messages sent)", "ru": "Топ менеджеров (отправлено сообщений)"},
    "mgr.recent_activity": {"en": "Recent leads", "ru": "Последние лиды"},
    "mgr.chat_breakdown": {"en": "Chat activity", "ru": "Активность чатов"},
    "mgr.incoming": {"en": "From users", "ru": "От пользователей"},
    "mgr.outgoing": {"en": "From managers/bot", "ru": "От менеджеров/бота"},
    "mgr.profile_coverage": {"en": "Telegram data coverage", "ru": "Полнота данных Telegram"},
    "mgr.with_phone": {"en": "With phone number", "ru": "С телефоном"},
    "mgr.with_location": {"en": "With location", "ru": "С локацией"},
    "mgr.manager": {"en": "Manager", "ru": "Менеджер"},
    "mgr.lead": {"en": "Lead", "ru": "Лид"},
    "mgr.leads": {"en": "Leads", "ru": "Лидов"},
    "mgr.messages": {"en": "Messages", "ru": "Сообщений"},
    "mgr.none_data": {"en": "No data yet", "ru": "Данных пока нет"},

    # ====================================================== статусы и родство
    # канонические статусы (цвета карточек менеджера — см. LeadStatus.CANONICAL)
    "status_name.visitor": {"en": "Visitor", "ru": "Посетитель"},
    "status_name.order": {"en": "Order", "ru": "Заявка"},
    "status_name.work": {"en": "In work", "ru": "В работе"},
    "status_name.lead": {"en": "Lead", "ru": "Лид"},
    # устаревшие названия (маппинг для старых записей в БД)
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
    "work": "status_name.work",
    "lead": "status_name.lead",
    # legacy aliases kept so old DB rows still render nicely
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
