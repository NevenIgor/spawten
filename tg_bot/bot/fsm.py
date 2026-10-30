"""FSM states and step definitions for the multi-step lead form.

User-visible strings (``question`` / ``label``) are translation keys resolved
through :mod:`bot.i18n` lazily via :func:`step_question` / :func:`step_label`,
so switching languages never breaks the internal keys used by handlers.
"""
from aiogram.fsm.state import State, StatesGroup

from bot.i18n import t


class LeadForm(StatesGroup):
    """One state per form step + review state."""

    relative_full_name = State()      # 1
    relative_birth_date = State()     # 2
    relative_workplace = State()      # 3
    relative_location = State()       # 4
    photo = State()                   # 5
    additional_info = State()         # 6
    relationship = State()            # 7
    full_name = State()               # 8
    workplace = State()               # 9
    contact_phone = State()           # 10
    review = State()                  # 11


STEPS: list[dict] = [
    {
        "state": LeadForm.relative_full_name,
        "key": "relative_full_name",
        "label_key": "label_relative_full_name",
        "question_key": "q_relative_full_name",
        "kind": "text",
        "required": True,
    },
    {
        "state": LeadForm.relative_birth_date,
        "key": "relative_birth_date",
        "label_key": "label_relative_birth_date",
        "question_key": "q_relative_birth_date",
        "kind": "date",
        "required": True,
    },
    {
        "state": LeadForm.relative_workplace,
        "key": "relative_workplace",
        "label_key": "label_relative_workplace",
        "question_key": "q_relative_workplace",
        "kind": "text",
        "required": False,
    },
    {
        "state": LeadForm.relative_location,
        "key": "relative_location",
        "label_key": "label_relative_location",
        "question_key": "q_relative_location",
        "kind": "text",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.photo,
        "key": "photo",
        "label_key": "label_photo",
        "question_key": "q_photo",
        "kind": "photo",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.additional_info,
        "key": "additional_info",
        "label_key": "label_additional_info",
        "question_key": "q_additional_info",
        "kind": "media_or_text",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.relationship,
        "key": "relationship",
        "label_key": "label_relationship",
        "question_key": "q_relationship",
        "kind": "relationship",
        "required": False,
    },
    {
        "state": LeadForm.full_name,
        "key": "full_name",
        "label_key": "label_full_name",
        "question_key": "q_full_name",
        "kind": "text",
        "required": True,
    },
    {
        "state": LeadForm.workplace,
        "key": "workplace",
        "label_key": "label_workplace",
        "question_key": "q_workplace",
        "kind": "text",
        "required": False,
    },
    {
        "state": LeadForm.contact_phone,
        "key": "contact_phone",
        "label_key": "label_contact_phone",
        "question_key": "q_contact_phone",
        "kind": "phone",
        "required": True,
    },
]

REVIEW_STATE = LeadForm.review

STEP_BY_KEY = {s["key"]: s for s in STEPS}
STATE_TO_INDEX = {s["state"]: i for i, s in enumerate(STEPS)}
INDEX_TO_STATE = {i: s["state"] for i, s in enumerate(STEPS)}


def step_question(step: dict) -> str:
    """Return the translated question text for a step."""
    return t(step["question_key"])


def step_label(step: dict) -> str:
    """Return the translated review-screen label for a step."""
    return t(step["label_key"])
