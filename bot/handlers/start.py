"""/start, main menu and registration (with referral deep-links)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.models import User
from bot.keyboards.callbacks import MenuCB
from bot.keyboards.user import main_menu
from bot.services import users as users_service
from bot.utils.logger import get_logger
from bot.utils.texts import money, welcome_text

logger = get_logger("bot.start")
router = Router(name="start")


async def _apply_referral(
    session: AsyncSession, user: User, command: CommandObject
) -> None:
    """Handle /start ref_<id> deep links for the referral program."""
    payload = (command.args or "").strip()
    if not payload.startswith("ref_"):
        return
    try:
        referrer_id = int(payload.removeprefix("ref_"))
    except ValueError:
        return
    if await users_service.set_referrer(session, user, referrer_id):
        referrer = await users_service.get_by_id(session, referrer_id)
        if referrer:
            await users_service.add_balance(session, referrer, settings.referral_bonus)
            logger.info("User %s joined via referral from %s", user.telegram_id, referrer_id)


@router.message(CommandStart(deep_link=True))
async def start_with_payload(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    user: User,
    is_new_user: bool,
) -> None:
    if is_new_user:
        await _apply_referral(session, user, command)
    await message.answer(welcome_text(user), reply_markup=main_menu())


@router.message(CommandStart())
async def start(message: Message, user: User) -> None:
    await message.answer(welcome_text(user), reply_markup=main_menu())


@router.callback_query(MenuCB.filter(F.action == "home"))
async def back_to_menu(query: CallbackQuery, user: User) -> None:
    await query.message.edit_text(welcome_text(user), reply_markup=main_menu())
    await query.answer()


@router.message(F.text == "/menu")
async def menu_command(message: Message, user: User) -> None:
    await message.answer(welcome_text(user), reply_markup=main_menu())


@router.message(F.text == "/ref")
async def referral_link(message: Message, user: User) -> None:
    me = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{user.id}"
    await message.answer(
        "🎁 <b>Реферальная программа</b>\n\n"
        f"Приглашайте друзей и получайте по <b>{money(settings.referral_bonus)}</b> за каждого.\n\n"
        f"Ваша ссылка:\n<code>{link}</code>"
    )
