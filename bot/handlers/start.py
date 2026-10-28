"""/start, main menu, language selector, and registration (with referral deep-links)."""
from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.models import User
from bot.keyboards.callbacks import LanguageCB, MenuCB
from bot.keyboards.user import back_home, language_selection_kb, main_menu
from bot.services import users as users_service
from bot.utils.emojis import EMOJI_GIFT, EMOJI_LIGHTNING, ce
from bot.utils.logger import get_logger
from bot.utils.texts import (
    get_lang,
    language_prompt_text,
    money,
    welcome_text,
)
from bot.utils.ui import render_menu_step

logger = get_logger("bot.start")
router = Router(name="start")

BANNER_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "welcome.png"


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


async def _send_welcome(message: Message, user: User) -> None:
    # If user hasn't chosen language yet, ask first
    if not user.language_code:
        await message.answer(
            language_prompt_text(),
            reply_markup=language_selection_kb(),
            parse_mode="HTML",
        )
        return

    text = welcome_text(user)
    lang = get_lang(user)
    if BANNER_PATH.exists():
        try:
            await message.answer_photo(
                FSInputFile(str(BANNER_PATH)),
                caption=text,
                reply_markup=main_menu(lang),
                parse_mode="HTML",
            )
            return
        except Exception as e:
            logger.warning("Failed to send welcome banner photo: %s", e)
    await message.answer(text, reply_markup=main_menu(lang), parse_mode="HTML")


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
    await _send_welcome(message, user)


@router.message(CommandStart())
async def start(message: Message, user: User) -> None:
    await _send_welcome(message, user)


@router.callback_query(LanguageCB.filter())
async def handle_language_choice(
    query: CallbackQuery,
    callback_data: LanguageCB,
    session: AsyncSession,
    user: User,
) -> None:
    """Save selected language and present main menu."""
    await users_service.set_language(session, user, callback_data.code)
    await session.commit()
    await query.answer()

    # Delete language selection message and show welcome with banner
    if query.message:
        try:
            await query.message.delete()
        except Exception:
            pass
        await _send_welcome(query.message, user)


@router.callback_query(MenuCB.filter(F.action == "language"))
async def switch_language_menu(query: CallbackQuery) -> None:
    """Prompt user to change language."""
    await render_menu_step(
        query,
        language_prompt_text(),
        reply_markup=language_selection_kb(),
    )
    await query.answer()


@router.callback_query(MenuCB.filter(F.action == "home"))
async def back_to_menu(query: CallbackQuery, user: User) -> None:
    lang = get_lang(user)
    text = welcome_text(user)
    msg = query.message
    if msg and msg.photo:
        try:
            await msg.edit_caption(
                caption=text, reply_markup=main_menu(lang), parse_mode="HTML"
            )
            await query.answer()
            return
        except Exception:
            pass
    try:
        if msg:
            await msg.edit_text(
                text, reply_markup=main_menu(lang), parse_mode="HTML"
            )
    except Exception:
        if msg:
            await msg.delete()
            await _send_welcome(msg, user)
    await query.answer()


@router.callback_query(MenuCB.filter(F.action == "referral"))
async def referral_menu_callback(query: CallbackQuery, user: User) -> None:
    lang = get_lang(user)
    me = await query.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{user.id}"
    icon_gift = ce(EMOJI_GIFT, "🎁")
    bonus = money(settings.referral_bonus)

    if lang == "en":
        text = (
            f"{icon_gift} <b>SEO Store Referral Program</b>\n"
            f"────────────────────────\n"
            f"Invite friends and earn <b>{bonus}</b> to your balance "
            f"for every registered customer!\n\n"
            f"🔗 Your unique referral link:\n"
            f"<code>{link}</code>\n\n"
            f"<i>Bonus is credited immediately upon their first /start.</i>"
        )
    else:
        text = (
            f"{icon_gift} <b>Реферальна програма SEO Store</b>\n"
            f"────────────────────────\n"
            f"Запрошуйте друзів та отримуйте по <b>{bonus}</b> "
            f"на баланс за кожного зареєстрованого покупця!\n\n"
            f"🔗 Ваше унікальне посилання для запрошень:\n"
            f"<code>{link}</code>\n\n"
            f"<i>Бонус нараховується автоматично після першого переходу.</i>"
        )

    await render_menu_step(query, text, reply_markup=back_home(lang))
    await query.answer()


@router.message(F.text == "/menu")
async def menu_command(message: Message, user: User) -> None:
    await _send_welcome(message, user)


@router.message(F.text == "/ref")
async def referral_link(message: Message, user: User) -> None:
    lang = get_lang(user)
    me = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{user.id}"
    icon_gift = ce(EMOJI_GIFT, "🎁")
    bonus = money(settings.referral_bonus)

    if lang == "en":
        await message.answer(
            f"{icon_gift} <b>Referral Program</b>\n"
            f"────────────────────────\n"
            f"Share your link and get <b>{bonus}</b> for each friend:\n"
            f"<code>{link}</code>",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            f"{icon_gift} <b>Реферальна програма</b>\n"
            f"────────────────────────\n"
            f"Діліться посиланням та отримуйте по <b>{bonus}</b> за кожного друга:\n"
            f"<code>{link}</code>",
            parse_mode="HTML",
        )
