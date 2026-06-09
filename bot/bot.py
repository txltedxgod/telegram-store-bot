"""Application entrypoint: build the bot/dispatcher and start polling."""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import settings
from bot.database.engine import session_factory
from bot.handlers import get_main_router
from bot.middlewares import (
    DbSessionMiddleware,
    LoggingMiddleware,
    UserMiddleware,
)
from bot.utils.logger import get_logger, setup_logging

logger = get_logger("bot.main")


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="ref", description="Реферальная ссылка"),
            BotCommand(command="admin", description="Админ-панель"),
        ]
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    # Order matters: logging -> db session -> user resolution -> handlers.
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.update.outer_middleware(UserMiddleware())
    dp.include_router(get_main_router())
    return dp


async def on_startup(bot: Bot) -> None:
    if settings.seed_demo_data:
        from bot.database.seed import seed_demo_data

        async with session_factory() as session:
            created = await seed_demo_data(session)
            await session.commit()
            if created:
                logger.info("Seeded demo categories and products")
    await set_commands(bot)
    me = await bot.get_me()
    logger.info("Bot @%s started", me.username)


async def main() -> None:
    setup_logging(settings.log_level)
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()
    dp.startup.register(on_startup)
    try:
        await dp.start_polling(
            bot, allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
