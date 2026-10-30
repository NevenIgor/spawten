"""FSM states and step definitions for the multi-step lead form."""
from aiogram.fsm.state import State, StatesGroup


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
        "label": "Relative full name",
        "question": "Full name of the relative (Ivanov Ivan Ivanovich)",
        "kind": "text",
        "required": True,
    },
    {
        "state": LeadForm.relative_birth_date,
        "key": "relative_birth_date",
        "label": "Relative birth date",
        "question": "Date of birth (DD.MM.YYYY)",
        "kind": "date",
        "required": True,
    },
    {
        "state": LeadForm.relative_workplace,
        "key": "relative_workplace",
        "label": "Relative workplace",
        "question": "Place of work of the relative",
        "kind": "text",
        "required": False,
    },
    {
        "state": LeadForm.relative_location,
        "key": "relative_location",
        "label": "Relative location",
        "question": "Location of the relative",
        "kind": "text",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.photo,
        "key": "photo",
        "label": "Relative photo",
        "question": "Photo of the relative\nAttach a photo or press 'Skip'",
        "kind": "photo",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.additional_info,
        "key": "additional_info",
        "label": "Additional info",
        "question": (
            "Additional information\n"
            "Send text, a photo, a video note, a video — or press 'Skip'"
        ),
        "kind": "media_or_text",
        "required": False,
        "skippable": True,
    },
    {
        "state": LeadForm.relationship,
        "key": "relationship",
        "label": "Relationship",
        "question": (
            "Who are you to the relative?\n"
            "(choose one of the options or type your own variant)"
        ),
        "kind": "relationship",
        "required": False,
    },
    {
        "state": LeadForm.full_name,
        "key": "full_name",
        "label": "Your full name",
        "question": "Your full name",
        "kind": "text",
        "required": True,
    },
    {
        "state": LeadForm.workplace,
        "key": "workplace",
        "label": "Your workplace",
        "question": "What do you do? / Where do you work?",
        "kind": "text",
        "required": False,
    },
    {
        "state": LeadForm.contact_phone,
        "key": "contact_phone",
        "label": "Contact phone",
        "question": "Your contact phone number",
        "kind": "phone",
        "required": True,
    },
]

REVIEW_STATE = LeadForm.review

STEP_BY_KEY = {s["key"]: s for s in STEPS}
STATE_TO_INDEX = {s["state"]: i for i, s in enumerate(STEPS)}
INDEX_TO_STATE = {i: s["state"] for i, s in enumerate(STEPS)}
