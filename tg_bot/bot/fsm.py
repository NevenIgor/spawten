"""FSM states and step definitions for the multi-step lead form.

User-visible strings come from :mod:`bot.texts` (English only — the bot has
no translation layer; translations live in the Django subsystem).
"""
from aiogram.fsm.state import State, StatesGroup

from bot.texts import LABELS, QUESTIONS, text


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
        "label_key": text(LABELS["relative_full_name"],
        "question_key": text(QUESTIONS["relative_full_name"],
        "kind": "text",
        "required": True,
    },
    {
        "state": LeadForm.relative_birth_date,
        "key": "relative_birth_date",
        "label_key": text(LABELS["relative_birth_date"],
        "question_key": text(QUESTIONS["relative_birth_date"],
        "kind": "date",
        "required": True,
    },
    {
        "state": LeadForm.relative_workplace,
        "key": "relative_workplace",
        "label_key": text(LABELS["relative_workplace"],
        "question_key": text(QUESTIONS["relative_workplace"],
        "kind": "text",
        "required": False,
    },
    {
        "state": LeadForm.relative_location,
        "key": "relative_location",
        "label_key": text(LABELS["relative_location"],
        "question_key": text(QUESTIONS["relative_location"],
        "kind": "text",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.photo,
        "key": "photo",
        "label_key": text(LABELS["photo"],
        "question_key": text(QUESTIONS["photo"],
        "kind": "photo",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.additional_info,
        "key": "additional_info",
        "label_key": text(LABELS["additional_info"],
        "question_key": text(QUESTIONS["additional_info"],
        "kind": "media_or_text",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.relationship,
        "key": "relationship",
        "label_key": text(LABELS["relationship"],
        "question_key": text(QUESTIONS["relationship"],
        "kind": "relationship",
        "required": False,
    },
    {
        "state": LeadForm.full_name,
        "key": "full_name",
        "label_key": text(LABELS["full_name"],
        "question_key": text(QUESTIONS["full_name"],
        "kind": "text",
        "required": True,
    },
    {
        "state": LeadForm.workplace,
        "key": "workplace",
        "label_key": text(LABELS["workplace"],
        "question_key": text(QUESTIONS["workplace"],
        "kind": "text",
        "required": False,
    },
    {
        "state": LeadForm.contact_phone,
        "key": "contact_phone",
        "label_key": text(LABELS["contact_phone"],
        "question_key": text(QUESTIONS["contact_phone"],
        "kind": "phone",
        "required": True,
    },
]

REVIEW_STATE = LeadForm.review

STEP_BY_KEY = {s["key"]: s for s in STEPS}
STATE_TO_INDEX = {s["state"]: i for i, s in enumerate(STEPS)}
INDEX_TO_STATE = {i: s["state"] for i, s in enumerate(STEPS)}


def step_question(step: dict) -> str:
    """Return the question text for a step."""
    return step["question_key"]


def step_label(step: dict) -> str:
    """Return the review-screen label for a step."""
    return step["label_key"]
