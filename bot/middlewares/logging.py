"""Structured logging of incoming updates."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from bot.utils.logger import get_logger

logger = get_logger("bot.updates")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            inner = event.event
            if isinstance(inner, Message) and inner.from_user:
                logger.info(
                    "Message from %s (%s): %r",
                    inner.from_user.id,
                    inner.from_user.username,
                    (inner.text or inner.caption or "<non-text>")[:120],
                )
            elif isinstance(inner, CallbackQuery) and inner.from_user:
                logger.info(
                    "Callback from %s (%s): %s",
                    inner.from_user.id,
                    inner.from_user.username,
                    inner.data,
                )
        return await handler(event, data)
