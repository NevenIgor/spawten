"""Inline keyboards for the lead form FSM.

All button texts come from bot.translations — edit tg_bot/bot/translations.py
to translate the bot.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.translations import t

SKIP_CB = "form:skip"
RELATIONSHIP_PREFIX = "form:rel:"
BACK_CB = "form:back"
SUBMIT_CB = "form:submit"
EDIT_CB = "form:edit"
CANCEL_CB = "form:cancel"
PREV_ANSWER_PREFIX = "form:prev:"

START_FILL_CB = "form:start"
VIEW_REQUEST_CB = "form:view"

# Relationship variants: (translation key, value stored in DB / sent back).
RELATIONSHIP_VARIANTS = [
    ("rel_wife", "жена"),
    ("rel_mother", "мать"),
    ("rel_father", "отец"),
    ("rel_sister", "сестра"),
    ("rel_son", "сын"),
    ("rel_daughter", "дочь"),
]


def start_kb() -> InlineKeyboardMarkup:
    """Welcome keyboard with a single 'Fill in the data' button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_fill_form"), callback_data=START_FILL_CB)]
        ]
    )


def view_request_kb() -> InlineKeyboardMarkup:
    """Keyboard for users whose lead already exists with a non-visitor status."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_view_request"), callback_data=VIEW_REQUEST_CB)]
        ]
    )


def skip_kb(back: bool = False) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=t("btn_skip"), callback_data=SKIP_CB)]]
    if back:
        rows.append([InlineKeyboardButton(text=t("btn_back"), callback_data=BACK_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def relationship_kb(prior_value: str | None = None) -> InlineKeyboardMarkup:
    """Step 7: preset variants + free text; prior answer is highlighted."""
    rows = []
    row: list[InlineKeyboardButton] = []
    for key, value in RELATIONSHIP_VARIANTS:
        label = t(key)
        if prior_value and prior_value.lower() == value.lower():
            label = f"✅ {label}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"{RELATIONSHIP_PREFIX}{value}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t("btn_skip"), callback_data=SKIP_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def review_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_submit"), callback_data=SUBMIT_CB)],
            [InlineKeyboardButton(text=t("btn_edit"), callback_data=EDIT_CB)],
        ]
    )


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data=CANCEL_CB)]
        ]
    )


def previous_answers_kb(options: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """Keyboard with previously entered values (Edit mode). Empty -> 'Skip'.

    ``options`` is a list of (step_index, rendered_value).
    """
    rows = []
    for step, value in options:
        short = value if len(value) <= 32 else value[:29] + "…"
        rows.append(
            [InlineKeyboardButton(text=f"{short}", callback_data=f"{PREV_ANSWER_PREFIX}{step}")]
        )
    rows.append([InlineKeyboardButton(text=t("btn_new_or_skip"), callback_data=SKIP_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
