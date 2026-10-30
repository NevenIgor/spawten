"""Inline keyboards for the lead form FSM."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
    """Welcome keyboard with a single 'Fill in the data' button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Fill in the data", callback_data=START_FILL_CB)]
        ]
    )


def view_request_kb() -> InlineKeyboardMarkup:
    """Keyboard for users whose lead already exists with a non-visitor status."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="View request", callback_data=VIEW_REQUEST_CB)]
        ]
    )


def skip_kb(back: bool = False) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="⏭ Skip", callback_data=SKIP_CB)]]
    if back:
        rows.append([InlineKeyboardButton(text="◀ Back", callback_data=BACK_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def relationship_kb(prior_value: str | None = None) -> InlineKeyboardMarkup:
    """Step 7: preset variants + free text; prior answer is highlighted."""
    variants = ["Wife", "Mother", "Father", "Sister", "Son", "Daughter"]
    rows = []
    row: list[InlineKeyboardButton] = []
    for v in variants:
        label = f"✅ {v}" if prior_value and prior_value.lower() == v.lower() else v
        row.append(InlineKeyboardButton(text=label, callback_data=f"form:rel:{v}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⏭ Skip", callback_data=SKIP_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def review_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📨 Submit request", callback_data=SUBMIT_CB)],
            [InlineKeyboardButton(text="✏️ Edit", callback_data=EDIT_CB)],
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
    rows.append([InlineKeyboardButton(text="⏭ Enter new / Skip", callback_data=SKIP_CB)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
