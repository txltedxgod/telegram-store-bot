"""UI and message transition helpers for seamless navigation."""
from __future__ import annotations

from aiogram.types import CallbackQuery, InlineKeyboardMarkup


async def render_menu_step(
    query: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Transitions from photo welcome banner to text sections without Telegram API errors."""
    if query.message and query.message.photo:
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.answer(text, reply_markup=reply_markup)
    elif query.message:
        try:
            await query.message.edit_text(text, reply_markup=reply_markup)
        except Exception:
            await query.message.answer(text, reply_markup=reply_markup)
