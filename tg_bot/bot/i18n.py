"""Translation file for all user-facing bot texts (English / Russian).

How to translate
----------------
All strings the bot shows to users live in the ``TRANSLATIONS`` dict below.

* ``en`` — English (default language, used as fallback for missing keys).
* ``ru`` — Russian. **Edit only the values on the right side of the ``ru``
  section** to adjust wording; do not rename the keys.

Choose the active language via the environment variable ``BOT_LANGUAGE``
(``en`` or ``ru``, default ``en``) — see ``.env.example``.

Usage in code::

    from bot.i18n import t
    text = t("welcome")                       # current language
    text = t("btn_fill_request", lang="ru")   # explicit language

Missing keys fall back to English so the bot never crashes on a typo.
"""
import os

DEFAULT_LANG = "en"

# Active language: BOT_LANGUAGE=en|ru (default: en)
CURRENT_LANG = os.getenv("BOT_LANGUAGE", DEFAULT_LANG).strip().lower()
if CURRENT_LANG not in ("en", "ru"):
    CURRENT_LANG = DEFAULT_LANG

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # ------------------------------------------------------ welcome screen
        # Shown on /start when the user has NO record in DB or status 'visitor'.
        "welcome": "Test welcome message",
        # Shown on /start when the user already has a submitted request.
        "welcome_existing": "You have already filled in the request.",
        # Shown after pressing 'View request' when no data was found.
        "no_request": "No submitted request found. Press the button below "
                      "to fill it in.",

        # ---------------------------------------------------------- buttons
        "btn_fill_request": "Fill in the request",
        "btn_view_request": "View request",
        "btn_skip": "⏭ Skip",
        "btn_back": "◀ Back",
        "btn_submit": "📨 Submit request",
        "btn_edit": "✏️ Edit",
        "btn_cancel": "❌ Cancel",
        "btn_new_or_skip": "⏭ Enter new / Skip",

        # ------------------------------------------------------- form steps
        # Questions (sent as HTML, bold formatting is added automatically).
        "q_relative_full_name": "Full name of the relative (Ivanov Ivan Ivanovich)",
        "q_relative_birth_date": "Date of birth (DD.MM.YYYY)",
        "q_relative_workplace": "Place of work of the relative",
        "q_relative_location": "Location of the relative",
        "q_photo": "Photo of the relative\nAttach a photo or press 'Skip'",
        "q_additional_info": "Additional information\n"
                             "Send text, a photo, a video note, a video — or press 'Skip'",
        "q_relationship": "Who are you to the relative?\n"
                          "(choose one of the options or type your own variant)",
        "q_full_name": "Your full name",
        "q_workplace": "What do you do? / Where do you work?",
        "q_contact_phone": "Your contact phone number",

        # Review-screen labels for each step.
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

        # Relationship preset variants (step 7 keyboard).
        "rel_wife": "Wife",
        "rel_mother": "Mother",
        "rel_father": "Father",
        "rel_sister": "Sister",
        "rel_son": "Son",
        "rel_daughter": "Daughter",

        # --------------------------------------------------- review / results
        "review_header": "Please check the entered data:",
        "submitted": "Test request submission text",
        "view_request_header": "Your request:",

        # --------------------------------------------- validation / messages
        "err_required": "This field is required, please enter a value.",
        "err_not_skippable": "This field cannot be skipped",
        "err_date_format": "❌ Wrong date format. Please enter the date as "
                           "DD.MM.YYYY (example: 15.06.1980).",
        "err_phone_format": "❌ The phone number doesn't look valid. Please try "
                            "again (e.g. +7 900 123-45-67).",
        "ok_photo": "✅ Photo received!",
        "ok_attachment": "✅ Attachment received!",
        "msg_text_only": "Please send text for this step (or press Skip).",
        "msg_cancelled": "The form is closed. Send /start to begin again.",
        "msg_edit_intro": "Let's correct the data — each step will show your "
                          "previous answer.",
        "hint_previous_highlighted": "Your previous answer is highlighted ✅ — "
                                     "or type a new variant.",
        "hint_reuse_previous": "You can reuse your previous answer:",
        "render_attachment": "📎 attachment",
        "render_empty": "—",
        "err_save": "Something went wrong while saving. Try again later.",
    },
    "ru": {
        # ------------------------------------------------------ welcome screen
        # Показывается на /start, если пользователя НЕТ в БД или статус 'visitor'.
        "welcome": "Тестовое приветственное сообщение",
        # Показывается на /start, если заявка уже заполнена.
        "welcome_existing": "Вы уже заполнили заявку.",
        # Показывается при нажатии «Посмотреть заявку», если данных нет.
        "no_request": "Заполненная заявка не найдена. Нажмите кнопку ниже, "
                      "чтобы заполнить её.",

        # ---------------------------------------------------------- кнопки
        "btn_fill_request": "Заполнить заявку",
        "btn_view_request": "Посмотреть заявку",
        "btn_skip": "⏭ Пропустить",
        "btn_back": "◀ Назад",
        "btn_submit": "📨 Отправить заявку",
        "btn_edit": "✏️ Изменить",
        "btn_cancel": "❌ Отмена",
        "btn_new_or_skip": "⏭ Ввести новое / Пропустить",

        # ------------------------------------------------------- шаги формы
        "q_relative_full_name": "ФИО родственника (Иванов Иван Иванович)",
        "q_relative_birth_date": "Дата рождения (ДД.ММ.ГГГГ)",
        "q_relative_workplace": "Место работы родственника",
        "q_relative_location": "Местоположение родственника",
        "q_photo": "Фотография родственника\nПрикрепите фото или нажмите «Пропустить»",
        "q_additional_info": "Дополнительная информация\n"
                             "Отправьте текст, фото, видеосообщение, видео — "
                             "или нажмите «Пропустить»",
        "q_relationship": "Кем вы приходитесь родственнику?\n"
                          "(выберите один из вариантов или впишите свой)",
        "q_full_name": "Ваше ФИО",
        "q_workplace": "Чем вы занимаетесь? / Где вы работаете?",
        "q_contact_phone": "Ваш контактный номер телефона",

        # Подписи шагов на экране проверки.
        "label_relative_full_name": "ФИО родственника",
        "label_relative_birth_date": "Дата рождения родственника",
        "label_relative_workplace": "Место работы родственника",
        "label_relative_location": "Местоположение родственника",
        "label_photo": "Фото родственника",
        "label_additional_info": "Дополнительная информация",
        "label_relationship": "Кем приходится",
        "label_full_name": "Ваше ФИО",
        "label_workplace": "Ваше место работы",
        "label_contact_phone": "Контактный телефон",

        # Варианты родства (клавиатура шага 7).
        "rel_wife": "Жена",
        "rel_mother": "Мать",
        "rel_father": "Отец",
        "rel_sister": "Сестра",
        "rel_son": "Сын",
        "rel_daughter": "Дочь",

        # --------------------------------------------------- проверка / итог
        "review_header": "Проверьте введённые данные:",
        "submitted": "Текст об отправке заявки",
        "view_request_header": "Ваша заявка:",

        # --------------------------------------------- ошибки / сообщения
        "err_required": "Это обязательное поле, пожалуйста, введите значение.",
        "err_not_skippable": "Это поле нельзя пропустить",
        "err_date_format": "❌ Неверный формат даты. Введите дату как ДД.ММ.ГГГГ "
                           "(пример: 15.06.1980).",
        "err_phone_format": "❌ Номер телефона выглядит некорректно. Попробуйте "
                            "ещё раз (например: +7 900 123-45-67).",
        "ok_photo": "✅ Фото получено!",
        "ok_attachment": "✅ Вложение получено!",
        "msg_text_only": "Пожалуйста, отправьте текст для этого шага "
                         "(или нажмите «Пропустить»).",
        "msg_cancelled": "Форма закрыта. Отправьте /start, чтобы начать заново.",
        "msg_edit_intro": "Исправим данные — на каждом шаге будет показан ваш "
                          "прежний ответ.",
        "hint_previous_highlighted": "Ваш прежний ответ отмечен ✅ — или впишите "
                                     "новый вариант.",
        "hint_reuse_previous": "Можно использовать прежний ответ:",
        "render_attachment": "📎 вложение",
        "render_empty": "—",
        "err_save": "При сохранении произошла ошибка. Попробуйте позже.",
    },
}


def set_language(lang: str) -> None:
    """Switch the active language at runtime ('en' or 'ru')."""
    global CURRENT_LANG
    lang = (lang or DEFAULT_LANG).strip().lower()
    if lang in TRANSLATIONS:
        CURRENT_LANG = lang


def get_language() -> str:
    return CURRENT_LANG


def t(key: str, *, lang: str | None = None) -> str:
    """Return the translated string for ``key``.

    Falls back to English, then to the key itself, so a missing translation
    never breaks the bot.
    """
    chosen = (lang or CURRENT_LANG).lower()
    table = TRANSLATIONS.get(chosen) or TRANSLATIONS[DEFAULT_LANG]
    if key in table:
        return table[key]
    return TRANSLATIONS[DEFAULT_LANG].get(key, key)
