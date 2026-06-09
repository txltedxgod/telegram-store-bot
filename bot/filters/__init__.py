"""Reusable aiogram filters."""
from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.config import settings
from bot.database.models import User


class IsAdmin(BaseFilter):
    """Allow handlers only for configured admins or DB-flagged admins.

    The current ``User`` is injected by ``UserMiddleware`` and received here as a
    keyword argument (aiogram passes middleware data to filters).
    """

    async def __call__(
        self, event: TelegramObject, user: User | None = None
    ) -> bool:
        telegram_id: int | None = None
        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            telegram_id = event.from_user.id
        if telegram_id is not None and settings.is_admin(telegram_id):
            return True
        return bool(user and user.is_admin)


__all__ = ["IsAdmin"]
