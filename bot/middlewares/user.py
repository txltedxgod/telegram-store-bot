"""Resolve (and lazily register) the current user for every update."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.services import users as users_service
from bot.utils.logger import get_logger

logger = get_logger("bot.users")


class UserMiddleware(BaseMiddleware):
    """Inject ``user`` and ``is_new_user`` into handler data.

    Must run *after* :class:`DbSessionMiddleware` so a session is available.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, Update):
            inner = event.event
            if isinstance(inner, (Message, CallbackQuery)):
                tg_user = inner.from_user

        session: AsyncSession | None = data.get("session")
        if tg_user is not None and session is not None and not tg_user.is_bot:
            user, created = await users_service.get_or_create_user(
                session,
                telegram_id=tg_user.id,
                username=tg_user.username,
                full_name=tg_user.full_name,
                is_admin=settings.is_admin(tg_user.id),
            )
            data["user"] = user
            data["is_new_user"] = created
            if created:
                logger.info("User %s registered", tg_user.id)
            if user.is_blocked:
                # Silently drop updates from blocked users.
                return None
        return await handler(event, data)
