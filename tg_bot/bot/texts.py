"""Тексты Telegram-бота (en + ru).

Это обычный файл со строками, а не система переводов: чтобы изменить любую
фразу бота — просто отредактируйте нужную строку ниже.

Каждая надпись хранится парой ``("en", "ru")``; активный язык задаётся
переменной окружения ``BOT_LANGUAGE`` (``en`` | ``ru``, по умолчанию ``en``).
Если русской строки нет, используется английская.

Перевод Django-подсистемы живёт отдельно: ``api/core/translations.py``.
"""

# Shown on /start when the user has NO record in DB or status is 'visitor'.
import os

DEFAULT_LANG = "ru"

# Активный язык сообщений бота: BOT_LANGUAGE=en|ru (по умолчанию en)
CURRENT_LANG = os.getenv("BOT_LANGUAGE", DEFAULT_LANG).strip().lower()
if CURRENT_LANG not in ("en", "ru"):
    CURRENT_LANG = DEFAULT_LANG


def _pair(en: str, ru: str) -> dict[str, str]:
    return {"en": en, "ru": ru}


def text(pair: dict[str, str]) -> str:
    """Вернуть строку на активном языке (fallback — английский)."""
    return pair.get(CURRENT_LANG) or pair["en"]


# ------------------------------------------------------------- welcome screen
# Shown on /start when the user has NO record in DB or status is 'visitor'.
WELCOME = _pair(
    "Test welcome message",
    """Тестовое приветственное сообщение""",
)

# Shown on /start when the user already has a submitted request.
WELCOME_EXISTING = _pair(
    "You have already filled in the request.",
    "Вы уже заполнили заявку.",
)

# Shown after pressing 'View request' when no data was found.
NO_REQUEST = _pair(
    "No submitted request found. Press the button below to fill it in.",
    "Заполненная заявка не найдена. Нажмите кнопку ниже, чтобы заполнить её.",
)

# ------------------------------------------------------------------- buttons
BTN_FILL_REQUEST = _pair("Fill in the request", "Заполнить заявку")
BTN_VIEW_REQUEST = _pair("View request", "Посмотреть заявку")
BTN_SKIP = _pair("⏭ Skip", "⏭ Пропустить")
BTN_BACK = _pair("◀ Back", "◀ Назад")
BTN_SUBMIT = _pair("📨 Submit request", "📨 Отправить заявку")
BTN_EDIT = _pair("✏️ Edit", "✏️ Изменить")
BTN_CANCEL = _pair("❌ Cancel", "❌ Отмена")
BTN_NEW_OR_SKIP = _pair("⏭ Enter new / Skip", "⏭ Пропустить")

# --------------------------------------------- form step questions (by key)
QUESTIONS = {
    "relative_full_name": _pair(
        "Full name of the relative (Ivanov Ivan Ivanovich)",
        "ФИО родственника (Иванов Иван Иванович)",
    ),
    "relative_birth_date": _pair(
        "Date of birth (DD.MM.YYYY)",
        "Дата рождения (ДД.ММ.ГГГГ)",
    ),
    "relative_workplace": _pair(
        "Place of work of the relative",
        "Место работы родственника",
    ),
    "relative_location": _pair(
        "Location of the relative",
        "Местоположение родственника",
    ),
    "photo": _pair(
        "Photo of the relative\nAttach a photo or press 'Skip'",
        "Фотография родственника\nПрикрепите фото или нажмите «Пропустить»",
    ),
    "additional_info": _pair(
        "Additional information\n"
        "Send text, a photo, a video note, a video — or press 'Skip'",
        "Дополнительная информация\n"
        "Отправьте текст, фото, видеосообщение, видео — или нажмите «Пропустить»",
    ),
    "relationship": _pair(
        "Who are you to the relative?\n"
        "(choose one of the options or type your own variant)",
        "Кем вы приходитесь родственнику?\n"
        "(выберите один из вариантов или впишите свой)",
    ),
    "full_name": _pair("Your full name", "Ваше ФИО"),
    "workplace": _pair(
        "What do you do? / Where do you work?",
        "Чем вы занимаетесь? / Где вы работаете?",
    ),
    "contact_phone": _pair("Your contact phone number", "Ваш контактный номер телефона"),
}

# ------------------------------------------- review-screen labels (by key)
LABELS = {
    "relative_full_name": _pair("Relative full name", "ФИО родственника"),
    "relative_birth_date": _pair("Relative birth date", "Дата рождения родственника"),
    "relative_workplace": _pair("Relative workplace", "Место работы родственника"),
    "relative_location": _pair("Relative location", "Местоположение родственника"),
    "photo": _pair("Relative photo", "Фото родственника"),
    "additional_info": _pair("Additional info", "Дополнительная информация"),
    "relationship": _pair("Relationship", "Кем приходится"),
    "full_name": _pair("Your full name", "Ваше ФИО"),
    "workplace": _pair("Your workplace", "Ваше место работы"),
    "contact_phone": _pair("Contact phone", "Контактный телефон"),
}

# Relationship preset variants (step 7 keyboard): canonical value -> label.
RELATIONSHIP_VARIANTS = [
    ("Wife", _pair("Wife", "Жена")),
    ("Mother", _pair("Mother", "Мать")),
    ("Father", _pair("Father", "Отец")),
    ("Sister", _pair("Sister", "Сестра")),
    ("Son", _pair("Son", "Сын")),
    ("Daughter", _pair("Daughter", "Дочь")),
]

# -------------------------------------------------------- review / results
REVIEW_HEADER = _pair("Please check the entered data:", "Проверьте введённые данные:")
SUBMITTED = _pair("Test request submission text", "Текст об отправке заявки")
VIEW_REQUEST_HEADER = _pair("Your request:", "Ваша заявка:")

# --------------------------------------------------- validation / messages
ERR_REQUIRED = _pair(
    "This field is required, please enter a value.",
    "Это обязательное поле, пожалуйста, введите значение.",
)
ERR_NOT_SKIPPABLE = _pair("This field cannot be skipped", "Это поле нельзя пропустить")
ERR_NO_PREVIOUS = _pair(
    "There is no previous answer to reuse here.",
    "Здесь нет прежнего ответа, который можно было бы использовать.",
)
ERR_DATE_FORMAT = _pair(
    "❌ Wrong date format. Please enter the date as DD.MM.YYYY (example: 15.06.1980).",
    "❌ Неверный формат даты. Введите дату как ДД.ММ.ГГГГ (пример: 15.06.1980).",
)
ERR_PHONE_FORMAT = _pair(
    "❌ The phone number doesn't look valid. Please try again (e.g. +7 900 123-45-67).",
    "❌ Номер телефона выглядит некорректно. Попробуйте ещё раз (например: +7 900 123-45-67).",
)
OK_PHOTO = _pair("✅ Photo received!", "✅ Фото получено!")
OK_ATTACHMENT = _pair("✅ Attachment received!", "✅ Вложение получено!")
MSG_TEXT_ONLY = _pair(
    "Please send text for this step (or press Skip).",
    "Пожалуйста, отправьте текст для этого шага (или нажмите «Пропустить»).",
)
MSG_CANCELLED = _pair(
    "The form is closed. Send /start to begin again.",
    "Форма закрыта. Отправьте /start, чтобы начать заново.",
)
MSG_EDIT_INTRO = _pair(
    "Let's correct the data — each step will show your previous answer.",
    "Исправим данные — на каждом шаге будет показан ваш прежний ответ.",
)
HINT_PREVIOUS_HIGHLIGHTED = _pair(
    "Your previous answer is highlighted ✅ — or type a new variant.",
    "Ваш прежний ответ отмечен ✅ — или впишите новый вариант.",
)
HINT_REUSE_PREVIOUS = _pair(
    "You can reuse your previous answer:",
    "Можно использовать прежний ответ:",
)
HINT_TYPE_TO_REPLACE = _pair(
    "(this step is required — type a message to enter a new value)",
    "(шаг обязателен — чтобы ввести новое, просто напишите сообщение)",
)
RENDER_ATTACHMENT = _pair("📎 attachment", "📎 вложение")
RENDER_EMPTY = _pair("—", "—")
ERR_SAVE = _pair(
    "Something went wrong while saving. Try again later.",
    "При сохранении произошла ошибка. Попробуйте позже.",
)
