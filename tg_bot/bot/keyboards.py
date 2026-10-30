"""Inline keyboards for the lead form FSM (labels come from bot.texts)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.texts import (
    BTN_BACK,
    BTN_CANCEL,
    BTN_EDIT,
    BTN_FILL_REQUEST,
    BTN_NEW_OR_SKIP,
    BTN_SKIP,
    BTN_SUBMIT,
    BTN_VIEW_REQUEST,
    RELATIONSHIP_VARIANTS,
    text,
)

SKIP_CB = "form:skip"
RELATIONSHIP_PREFIX = "form:rel:"
BACK_CB = "form:back"
SUBMIT_CB = "form:submit"
EDIT_CB = "form:edit"
CANCEL_CB = "form:cancel"
PREV_ANSWER_PREFIX = "form:prev:"

START_FILL_CB = "form:start"
VIEW_REQUEST_CB = "form:view"


def start_kb() -> InlineKeyboardMarkup:
    """Welcome keyboard for a new/visitor user: 'Fill in the request'."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text(BTN_FILL_REQUEST), callback_data=START_FILL_CB)]
        ]
    )


def existing_kb() -> InlineKeyboardMarkup:
    """Welcome keyboard for a user with a submitted request: 'View request'."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text(BTN_VIEW_REQUEST), callback_data=VIEW_REQUEST_CB)]
        ]
    )


def fill_request_kb() -> InlineKeyboardMarkup:
    """Standalone 'Fill in the request' button (e.g. after viewing fails)."""
    return start_kb()


def skip_kb(back: bool = False) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=text(BTN_SKIP), callback_data=SKIP_CB)]]
    if back:
        rows.append([InlineKeyboardButton(text=text(BTN_BACK), callback_data=BACK_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def relationship_kb(prior_value: str | None = None, edit_mode: bool = False) -> InlineKeyboardMarkup:
    """Step 7: preset variants + free text (typed message counts as "own" variant).

    There is deliberately no "Skip" button on this step — the user must pick a
    preset variant or type their own. In edit mode the previous answer is shown
    as an extra highlighted button that reuses it (plus "Enter new / Skip").

    Button labels are localized, but callback_data keeps the canonical
    English value so stored DB data stays consistent across languages.
    """
    rows = []
    row: list[InlineKeyboardButton] = []
    for value, label_pair in RELATIONSHIP_VARIANTS:
        label = text(label_pair)
        display = f"✅ {label}" if prior_value and prior_value.lower() == value.lower() else label
        row.append(InlineKeyboardButton(text=display, callback_data=f"{RELATIONSHIP_PREFIX}{value}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if edit_mode and prior_value:
        # Previous answer may not match any preset variant — offer it as its
        # own one-tap button so it can be reused without retyping.
        reuse_label = f"♻️ ✅ {prior_value}"
        rows.append([
            InlineKeyboardButton(text=reuse_label, callback_data=f"{PREV_ANSWER_PREFIX}reuse"),
            InlineKeyboardButton(text=text(BTN_NEW_OR_SKIP), callback_data=SKIP_CB),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def review_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text(BTN_SUBMIT), callback_data=SUBMIT_CB)],
            [InlineKeyboardButton(text=text(BTN_EDIT), callback_data=EDIT_CB)],
        ]
    )


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text(BTN_CANCEL), callback_data=CANCEL_CB)]
        ]
    )


def previous_answers_kb(options: list[tuple[int, str]], allow_skip: bool = True) -> InlineKeyboardMarkup:
    """Keyboard with previously entered values (Edit mode).

    ``options`` is a list of (step_index, rendered_value).
    ``allow_skip`` adds the 'Enter new / Skip' button; it is disabled for
    required steps where there is nothing to skip — typing a message always
    enters a new value instead.
    """
    rows = []
    for step, value in options:
        short = value if len(value) <= 32 else value[:29] + "…"
        rows.append(
            [InlineKeyboardButton(text=f"♻️ {short}", callback_data=f"{PREV_ANSWER_PREFIX}{step}")]
        )
    if allow_skip:
        rows.append([InlineKeyboardButton(text=text(BTN_NEW_OR_SKIP), callback_data=SKIP_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
