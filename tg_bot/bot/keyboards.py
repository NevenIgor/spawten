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


def _localize_relationship(value: str | None) -> str | None:
    """Map a stored relationship value to the active language.

    Callback data keeps canonical English values for DB consistency, but the
    keyboard must never show an English label next to localized ones (e.g.
    'Мать' + 'Mother') — so a previously stored value is translated back.
    The match is checked against both the canonical name and every localized
    label, so legacy rows that stored the user's on-screen label ('Мать')
    are also recognized as the corresponding variant.
    """
    if not value:
        return value
    needle = value.strip().lower()
    for canonical, label_pair in RELATIONSHIP_VARIANTS:
        candidates = {canonical.lower(), *(s.strip().lower() for s in label_pair.values() if s)}
        if needle in candidates:
            return text(label_pair)
    return value


def relationship_kb(prior_value: str | None = None, edit_mode: bool = False) -> InlineKeyboardMarkup:
    """Step 7: preset variants + free text (typed message counts as "own" variant).

    There is deliberately no "Skip" button on this step — the user must pick a
    preset variant or type their own. In edit mode the previous answer is shown
    as its own highlighted ♻️ reuse button; entering a new value is done by
    typing a message (or tapping another variant), so there is no skip option.

    Button labels are localized, but callback_data keeps the canonical
    English value so stored DB data stays consistent across languages.
    """
    prior_local = _localize_relationship(prior_value)
    rows = []
    row: list[InlineKeyboardButton] = []
    for value, label_pair in RELATIONSHIP_VARIANTS:
        label = text(label_pair)
        display = f"✅ {label}" if prior_local and prior_local.lower() == label.lower() else label
        row.append(InlineKeyboardButton(text=display, callback_data=f"{RELATIONSHIP_PREFIX}{value}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if edit_mode and prior_local:
        # Previous answer may not match any preset variant — offer it as its
        # own one-tap button so it can be reused without retyping.
        reuse_label = f"♻️ ✅ {prior_local}"
        rows.append([
            InlineKeyboardButton(text=reuse_label, callback_data=f"{PREV_ANSWER_PREFIX}reuse")
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
