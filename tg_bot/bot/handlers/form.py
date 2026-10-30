"""Lead form FSM handlers: step-by-step data collection with validation."""
import logging
import os
import uuid
from datetime import date

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database import get_lead_snapshot, save_lead_from_form
from bot.db_utils import run_sync
from bot.fsm import REVIEW_STATE, STEPS, step_label, step_question
from bot.keyboards import (
    EDIT_CB,
    PREV_ANSWER_PREFIX,
    RELATIONSHIP_PREFIX,
    SKIP_CB,
    START_FILL_CB,
    SUBMIT_CB,
    VIEW_REQUEST_CB,
    previous_answers_kb,
    relationship_kb,
    review_kb,
    skip_kb,
)
from bot.texts import NO_REQUEST, SUBMITTED, VIEW_REQUEST_HEADER, WELCOME_SEEN
from bot.translations import t
from bot.validation import format_date, parse_date, validate_phone

logger = logging.getLogger(__name__)

router = Router()

MEDIA_DIR = os.getenv("BOT_MEDIA_DIR", "/media")


# ------------------------------------------------------------------ helpers


def _current_index(state_value: str | None) -> int | None:
    """Return index of the current step by its FSM state ('LeadForm:<key>')."""
    if not state_value or ":" not in state_value:
        return None
    key = state_value.split(":", 1)[1]
    for i, s in enumerate(STEPS):
        if s["key"] == key:
            return i
    return None


async def _ask_step(target_msg: Message | None, state: FSMContext, index: int,
                    *, from_callback: bool = False, cb: CallbackQuery | None = None,
                    as_new: bool = True) -> None:
    """Send the question for step ``index``; in edit mode offer previous answers."""
    step = STEPS[index]
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)
    prev = data.get(step["key"])

    text = f"<b>{step_question(step)}</b>"

    kb = None
    if step["kind"] == "relationship":
        kb = relationship_kb(prev if edit_mode else None)
        if edit_mode and prev:
            text += f"\n\n<i>{t('highlight_hint')}</i>"
    elif edit_mode and prev not in (None, "", []):
        rendered = _render_value(step, prev)
        kb = previous_answers_kb([(index, rendered)])
        text += f"\n\n<i>{t('reuse_hint')}</i>"
    elif step.get("skippable"):
        kb = skip_kb()

    if from_callback and cb and cb.message:
        if as_new:
            await cb.message.answer(text, reply_markup=kb)
        else:
            try:
                await cb.message.edit_text(text, reply_markup=kb)
            except Exception:  # message already has this content
                await cb.message.answer(text, reply_markup=kb)
    elif target_msg:
        if as_new:
            await target_msg.answer(text, reply_markup=kb)
        else:
            try:
                await target_msg.edit_text(text, reply_markup=kb)
            except Exception:
                await target_msg.answer(text, reply_markup=kb)
    await state.set_state(step["state"])


def _render_value(step: dict, value) -> str:
    if isinstance(value, date):
        return format_date(value)
    if isinstance(value, dict):
        return t("attachment_label")
    return str(value)


async def _advance(source: Message | CallbackQuery | None, state: FSMContext,
                   index: int) -> None:
    """Go to the next step or to review."""
    if index + 1 < len(STEPS):
        if isinstance(source, CallbackQuery):
            await _ask_step(None, state, index + 1, from_callback=True, cb=source)
        else:
            await _ask_step(source, state, index + 1)
    else:
        await _show_review(source, state)


async def _show_review(source: Message | CallbackQuery | None, state: FSMContext) -> None:
    data = await state.get_data()
    lines = []
    for step in STEPS:
        value = data.get(step["key"])
        if isinstance(value, date):
            value = format_date(value)
        if value in (None, ""):
            value = t("empty_value")
        lines.append(f"<b>{step_label(step)}:</b> {value}")
    text = f"<b>{t('review_header')}</b>\n\n" + "\n".join(lines)

    if isinstance(source, CallbackQuery) and source.message:
        await source.message.answer(text, reply_markup=review_kb())
    elif isinstance(source, Message):
        await source.answer(text, reply_markup=review_kb())
    await state.set_state(REVIEW_STATE)


async def _download(bot, file_id: str, prefix: str) -> str:
    """Download media into MEDIA_DIR, return relative path 'sub/name.ext'."""
    ext_map = {"photo": ".jpg", "video": ".mp4", "video_note": ".mp4",
               "animation": ".gif", "document": ".bin"}
    ext = ext_map.get(prefix, ".bin")
    rel_dir = f"bot-uploads/{uuid.uuid4().hex[:8]}"
    abs_dir = os.path.join(MEDIA_DIR, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(abs_dir, filename)
    f = await bot.get_file(file_id)
    await bot.download_file(f.file_path, dest)
    return f"{rel_dir}/{filename}"


# ------------------------------------------------------------------ entry point


@router.callback_query(StateFilter(None), F.data == START_FILL_CB)
async def cb_start_form(cb: CallbackQuery, state: FSMContext) -> None:
    """'Fill in the data' button on the welcome screen starts the wizard."""
    await state.update_data(tg_id=cb.from_user.id, edit_mode=False)
    await cb.answer()
    await _ask_step(None, state, 0, from_callback=True, cb=cb)


@router.message(StateFilter(None), F.text.lower() == "/cancel")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t("form_cancelled"))


# ------------------------------------------------------------------ text input


@router.message(
    StateFilter(*[s["state"] for s in STEPS]),
    F.text & ~F.text.startswith("/"),
)
async def handle_text(message: Message, state: FSMContext) -> None:
    index = _current_index(await state.get_state())
    if index is None:
        return
    step = STEPS[index]
    raw = (message.text or "").strip()

    if step["kind"] == "date":
        parsed = parse_date(raw)
        if parsed is None:
            await message.answer(t("err_date_format", example="15.06.1980"))
            return
        await state.update_data({step["key"]: parsed})
        await _advance(message, state, index)
        return

    if step["kind"] == "phone":
        phone = validate_phone(raw)
        if phone is None:
            await message.answer(t("err_phone_format", example="+7 900 123-45-67"))
            return
        await state.update_data({step["key"]: phone})
        await _advance(message, state, index)
        return

    if step["kind"] == "relationship":
        await state.update_data({step["key"]: raw})
        await _advance(message, state, index)
        return

    if step["kind"] == "media_or_text":
        await state.update_data({step["key"]: raw, step["key"] + "_media": ""})
        await _advance(message, state, index)
        return

    # plain text steps
    if step["required"] and not raw:
        await message.answer(t("err_required"))
        return
    await state.update_data({step["key"]: raw})
    await _advance(message, state, index)


# ------------------------------------------------------------------ media input


@router.message(
    StateFilter(*[s["state"] for s in STEPS]),
    F.photo | F.video | F.video_note | F.document | F.animation,
)
async def handle_media(message: Message, state: FSMContext, bot) -> None:
    index = _current_index(await state.get_state())
    if index is None:
        return
    step = STEPS[index]

    if step["kind"] == "photo":
        photo = message.photo[-1]
        path = await _download(bot, photo.file_id, "photo")
        await state.update_data({step["key"]: path})
        await message.answer(t("ok_photo"))
        await _advance(message, state, index)
        return

    if step["kind"] == "media_or_text":
        if message.photo:
            file_id, kind = message.photo[-1].file_id, "photo"
        elif message.video:
            file_id, kind = message.video.file_id, "video"
        elif message.video_note:
            file_id, kind = message.video_note.file_id, "video_note"
        elif message.animation:
            file_id, kind = message.animation.file_id, "animation"
        else:
            file_id, kind = message.document.file_id, "document"
        path = await _download(bot, file_id, kind)
        await state.update_data({step["key"]: f"📎 {kind}", step["key"] + "_media": path})
        await message.answer(t("ok_attachment"))
        await _advance(message, state, index)
        return

    # Media sent on a text-only step (e.g. photo on the 'additional info' question)
    if step["kind"] == "text" and not step["required"]:
        if message.photo:
            file_id, kind = message.photo[-1].file_id, "photo"
        elif message.video:
            file_id, kind = message.video.file_id, "video"
        elif message.video_note:
            file_id, kind = message.video_note.file_id, "video_note"
        elif message.animation:
            file_id, kind = message.animation.file_id, "animation"
        else:
            file_id, kind = message.document.file_id, "document"
        path = await _download(bot, file_id, kind)
        await state.update_data({step["key"]: "", step["key"] + "_media": path})
        await message.answer(t("ok_attachment"))
        await _advance(message, state, index)
        return

    await message.answer(t("err_text_only"))


# ------------------------------------------------------------------ callbacks


@router.callback_query(
    StateFilter(*[s["state"] for s in STEPS]),
    F.data == SKIP_CB,
)
async def cb_skip(cb: CallbackQuery, state: FSMContext) -> None:
    index = _current_index(await state.get_state())
    if index is None:
        return
    step = STEPS[index]
    if step["required"]:
        await cb.answer(t("err_cannot_skip"), show_alert=True)
        return
    await state.update_data({step["key"]: "", step["key"] + "_media": ""})
    await cb.answer()
    await _advance(cb, state, index)


@router.callback_query(
    StateFilter(*[s["state"] for s in STEPS]),
    F.data.strstartswith(PREV_ANSWER_PREFIX),
)
async def cb_use_previous(cb: CallbackQuery, state: FSMContext) -> None:
    """Edit mode: keep the previously entered value and move to the next step."""
    index = _current_index(await state.get_state())
    if index is None:
        return
    await cb.answer()
    await _advance(cb, state, index)


@router.callback_query(
    StateFilter(*[s["state"] for s in STEPS]),
    F.data.strstartswith(RELATIONSHIP_PREFIX),
)
async def cb_relationship(cb: CallbackQuery, state: FSMContext) -> None:
    value = cb.data.removeprefix(RELATIONSHIP_PREFIX)
    await state.update_data({"relationship": value})
    await cb.answer()
    await _advance(cb, state, 6)


# ------------------------------------------------------------------ review


@router.callback_query(REVIEW_STATE, F.data == SUBMIT_CB)
async def cb_submit(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("tg_id") or cb.from_user.id
    birth = data.get("relative_birth_date")
    if isinstance(birth, str):
        birth = parse_date(birth)

    try:
        await run_sync(
            save_lead_from_form,
            tg_id=tg_id,
            relative_full_name=data.get("relative_full_name", ""),
            relative_birth_date=birth,
            relative_workplace=data.get("relative_workplace", ""),
            relative_location=data.get("relative_location", ""),
            photo_path=data.get("photo") or None,
            additional_info=data.get("additional_info", ""),
            additional_media_path=data.get("additional_info_media") or None,
            relationship=data.get("relationship", ""),
            full_name=data.get("full_name", ""),
            workplace=data.get("workplace", ""),
            contact_phone=data.get("contact_phone", ""),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to save lead")
        await cb.answer(t("err_save_db"), show_alert=True)
        return

    await state.clear()
    await cb.message.edit_text(SUBMITTED)
    await cb.answer()


@router.callback_query(REVIEW_STATE, F.data == EDIT_CB)
async def cb_edit(cb: CallbackQuery, state: FSMContext) -> None:
    """Restart all steps keeping previous answers available on keyboards."""
    await state.update_data(edit_mode=True)
    await cb.answer()
    await cb.message.answer(t("edit_mode_intro"))
    await _ask_step(None, state, 0, from_callback=True, cb=cb)


# ------------------------------------------------------------------ view request


async def _send_request_snapshot(target: Message) -> None:
    """Render the saved lead from the DB and send it to the user."""
    try:
        rows = await run_sync(get_lead_snapshot, target.from_user.id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load lead snapshot")
        await target.answer(t("err_load_db"))
        return

    if not rows:
        await target.answer(NO_REQUEST)
        return

    lines = [f"<b>{VIEW_REQUEST_HEADER}</b>", ""]
    for label, value in rows:
        escaped_value = (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        lines.append(f"<b>{label}:</b> {escaped_value}")
    await target.answer("\n".join(lines))


@router.callback_query(StateFilter(None), F.data == VIEW_REQUEST_CB)
async def cb_view_request(cb: CallbackQuery) -> None:
    """'View request' button: show the data already saved in the database."""
    await cb.answer()
    if cb.message:
        await _send_request_snapshot(cb.message)
