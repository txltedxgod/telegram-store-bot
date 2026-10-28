"""UI and message transition helpers for seamless navigation across text, photos, and animated GIFs."""
from __future__ import annotations

from pathlib import Path
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup


async def render_menu_step(
    query: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Transitions from photo/GIF banners to text views without Telegram API errors."""
    msg = query.message
    if not msg:
        return

    is_media = bool(msg.photo or msg.animation or msg.video or msg.document)
    if is_media:
        try:
            await msg.delete()
        except Exception:
            pass
        await msg.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        try:
            await msg.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            try:
                await msg.delete()
            except Exception:
                pass
            await msg.answer(text, reply_markup=reply_markup, parse_mode="HTML")


async def render_animation_step(
    query: CallbackQuery,
    gif_path: Path,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Renders or replaces message with an animated GIF."""
    msg = query.message
    if not msg:
        return

    try:
        await msg.delete()
    except Exception:
        pass

    if gif_path.exists():
        try:
            await msg.answer_animation(
                FSInputFile(str(gif_path)),
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            return
        except Exception:
            pass

    await msg.answer(caption, reply_markup=reply_markup, parse_mode="HTML")
