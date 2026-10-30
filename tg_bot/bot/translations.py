"""Translation dictionaries for the Telegram bot.

How to edit / add a language
----------------------------
1. Every user-facing string has a unique key (see the ``en`` dictionary below —
   it is the reference list of keys).
2. To translate the bot into Russian, edit the ``ru`` dictionary: keep the
   KEYS unchanged, replace only the VALUES with Russian text.
3. To add a new language, copy the ``en`` dictionary, rename it (e.g. ``de``)
   and register it in the ``TRANSLATIONS`` mapping at the bottom of this file.

The active language is taken from the environment variable ``BOT_LANGUAGE``
(see docker-compose.yml / .env). Default: "ru".

Strings may contain {placeholders} — do not remove them, they are filled in
at runtime (e.g. "{value}" — previous answer, "{example}" — sample date).
"""

# --------------------------------------------------------------------------
# English (reference version)
# --------------------------------------------------------------------------
en = {
    # --- Welcome screen --------------------------------------------------
    "welcome": "Test welcome message",
    "btn_fill_form": "Fill in the data",
    "welcome_seen": "You have already submitted a request. You can view it below.",
    "btn_view_request": "View request",

    # --- Form questions (steps 1-10) --------------------------------------
    "q_relative_full_name": "Full name (Ivanov Ivan Ivanovich)",
    "q_relative_birth_date": "Date of birth (DD.MM.YYYY)",
    "q_relative_workplace": "Place of work",
    "q_relative_location": "Location",
    "q_photo": "Relative's photo\nAttach a photo or press 'Skip'",
    "q_additional_info": (
        "Additional information\n"
        "Send text, a photo, a video note, a video — or press 'Skip'"
    ),
    "q_relationship": (
        "Who are you to the relative?\n"
        "(choose one of the options or type your own variant)"
    ),
    "q_full_name": "Your full name",
    "q_workplace": "What do you do? / Where do you work?",
    "q_contact_phone": "Your contact phone number",

    # --- Review screen -----------------------------------------------------
    "review_header": "Please check the entered data:",
    "btn_submit": "📨 Submit request",
    "btn_edit": "✏️ Edit",
    "submitted": "Test request submission text",
    "edit_mode_intro": (
        "Let's correct the data — each step will show your previous answer."
    ),
    "reuse_hint": "You can reuse your previous answer:",
    "highlight_hint": (
        "Your previous answer is highlighted ✅ — or type a new variant."
    ),

    # --- Common buttons / hints --------------------------------------------
    "btn_skip": "⏭ Skip",
    "btn_back": "◀ Back",
    "btn_new_or_skip": "⏭ Enter new / Skip",
    "attachment_label": "📎 attachment",
    "empty_value": "—",

    # --- Relationship variants ----------------------------------------------
    "rel_wife": "Wife",
    "rel_mother": "Mother",
    "rel_father": "Father",
    "rel_sister": "Sister",
    "rel_son": "Son",
    "rel_daughter": "Daughter",

    # --- Field labels (used on the review & view screens) -------------------
    "label_relative_full_name": "Relative full name",
    "label_relative_birth_date": "Relative birth date",
    "label_relative_workplace": "Relative workplace",
    "label_relative_location": "Relative location",
    "label_photo": "Relative photo",
    "label_additional_info": "Additional info",
    "label_relationship": "Relationship",
    "label_full_name": "Your full name",
    "label_workplace": "Your workplace",
    "label_contact_phone": "Contact phone",
    "label_tg_id": "Telegram ID",
    "label_status": "Status",
    "label_created": "Created",
    "label_first_contact": "First contact date",

    # --- Validation & service messages ---------------------------------------
    "err_date_format": (
        "❌ Wrong date format. Please enter the date as DD.MM.YYYY "
        "(example: {example})."
    ),
    "err_phone_format": (
        "❌ The phone number doesn't look valid. Please try again "
        "(e.g. {example})."
    ),
    "err_required": "This field is required, please enter a value.",
    "err_cannot_skip": "This field cannot be skipped",
    "err_text_only": "Please send text for this step (or press Skip).",
    "ok_photo": "✅ Photo received!",
    "ok_attachment": "✅ Attachment received!",
    "form_cancelled": "The form is closed. Send /start to begin again.",
    "err_save_db": "Something went wrong while saving. Try again later.",
    "err_load_db": (
        "Something went wrong while loading your request. Please try again later."
    ),

    # --- View request screen ---------------------------------------------------
    "view_request_header": "Your request:",
    "no_request": "No saved request found. Send /start and fill in the form.",
}

# --------------------------------------------------------------------------
# Русский (перевод — правьте значения, ключи не меняйте)
# --------------------------------------------------------------------------
ru = {
    # --- Приветственный экран -----------------------------------------------
    "welcome": "Тест приветственного сообщения",
    "btn_fill_form": "Заполнить данные",
    "welcome_seen": "Вы уже отправили заявку. Вы можете посмотреть её ниже.",
    "btn_view_request": "Посмотреть заявку",

    # --- Вопросы формы (шаги 1-10) ---------------------------------------------
    "q_relative_full_name": "ФИО (Иванов Иван Иванович)",
    "q_relative_birth_date": "Дата рождения (ДД.ММ.ГГГГ)",
    "q_relative_workplace": "Место работы",
    "q_relative_location": "Место нахождения",
    "q_photo": "Фото родственника\nПрикрепите фото или нажмите «Пропустить»",
    "q_additional_info": (
        "Дополнительная информация\n"
        "Отправьте текст, фото, видеокружок, видео — или нажмите «Пропустить»"
    ),
    "q_relationship": (
        "Кем вы приходитесь родственнику?\n"
        "(выберите из предложенного или напишите свой вариант)"
    ),
    "q_full_name": "Ваше ФИО",
    "q_workplace": "Кем вы работаете?",
    "q_contact_phone": "Ваш контактный номер телефона",

    # --- Экран проверки -----------------------------------------------------------
    "review_header": "Проверьте правильность введенных данных:",
    "btn_submit": "📨 Отправить заявку",
    "btn_edit": "✏️ Изменить",
    "submitted": "Тестовый текст отправки заявки",
    "edit_mode_intro": (
        "Давайте исправим данные — на каждом шаге будет показан ваш прошлый ответ."
    ),
    "reuse_hint": "Можно использовать предыдущий ответ:",
    "highlight_hint": (
        "Ваш предыдущий ответ отмечен ✅ — или напишите новый вариант."
    ),

    # --- Общие кнопки / подсказки --------------------------------------------------
    "btn_skip": "⏭ Пропустить",
    "btn_back": "◀ Назад",
    "btn_new_or_skip": "⏭ Ввести новое / Пропустить",
    "attachment_label": "📎 вложение",
    "empty_value": "—",

    # --- Варианты родства -------------------------------------------------------------
    "rel_wife": "жена",
    "rel_mother": "мать",
    "rel_father": "отец",
    "rel_sister": "сестра",
    "rel_son": "сын",
    "rel_daughter": "дочь",

    # --- Подписи полей (экраны проверки и просмотра) ---------------------------------
    "label_relative_full_name": "ФИО родственника",
    "label_relative_birth_date": "Дата рождения родственника",
    "label_relative_workplace": "Место работы родственника",
    "label_relative_location": "Место нахождения родственника",
    "label_photo": "Фото родственника",
    "label_additional_info": "Доп. информация",
    "label_relationship": "Кем приходится",
    "label_full_name": "ФИО",
    "label_workplace": "Место работы",
    "label_contact_phone": "Контактный телефон",
    "label_tg_id": "Telegram ID",
    "label_status": "Статус",
    "label_created": "Создан",
    "label_first_contact": "Дата первого обращения",

    # --- Валидация и служебные сообщения ----------------------------------------------
    "err_date_format": (
        "❌ Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ "
        "(пример: {example})."
    ),
    "err_phone_format": (
        "❌ Номер телефона выглядит некорректно. Попробуйте ещё раз "
        "(например, {example})."
    ),
    "err_required": "Это поле обязательно для заполнения, введите значение.",
    "err_cannot_skip": "Это поле нельзя пропустить",
    "err_text_only": "Для этого шага отправьте текст (или нажмите «Пропустить»).",
    "ok_photo": "✅ Фото получено!",
    "ok_attachment": "✅ Вложение получено!",
    "form_cancelled": "Форма закрыта. Отправьте /start, чтобы начать заново.",
    "err_save_db": "Что-то пошло не так при сохранении. Попробуйте позже.",
    "err_load_db": (
        "Не удалось загрузить вашу заявку. Попробуйте позже."
    ),

    # --- Экран просмотра заявки ----------------------------------------------------------
    "view_request_header": "Ваша заявка:",
    "no_request": "Сохранённая заявка не найдена. Отправьте /start и заполните форму.",
}

# --------------------------------------------------------------------------
# Registry & lookup
# --------------------------------------------------------------------------
TRANSLATIONS: dict[str, dict[str, str]] = {"en": en, "ru": ru}

DEFAULT_LANGUAGE = "ru"


def set_language(lang: str) -> None:
    """Set the active language (falls back to DEFAULT_LANGUAGE if unknown)."""
    global _current
    _current = lang if lang in TRANSLATIONS else DEFAULT_LANGUAGE


def t(key: str, **kwargs) -> str:
    """Return the translated string for ``key`` in the active language.

    Falls back to English if the key is missing in the current language,
    and returns the key itself if it is unknown everywhere.
    """
    table = TRANSLATIONS.get(_current, {})
    text = table.get(key) or en.get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


_current = DEFAULT_LANGUAGE
