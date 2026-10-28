"""/start, main menu, language selector, and animated video/GIF welcome loop."""
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
from bot.utils.emojis import EMOJI_GIFT, ce
from bot.utils.logger import get_logger
from bot.utils.texts import (
    get_lang,
    language_prompt_text,
    money,
    welcome_text,
)
from bot.utils.ui import render_animation_step, render_menu_step

logger = get_logger("bot.start")
router = Router(name="start")

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
WELCOME_MP4_PATH = ASSETS_DIR / "welcome.mp4"
WELCOME_GIF_PATH = ASSETS_DIR / "welcome.gif"
_WELCOME_FILE_ID: str | None = None


def get_welcome_media_path() -> Path | None:
    if WELCOME_MP4_PATH.exists():
        return WELCOME_MP4_PATH
    if WELCOME_GIF_PATH.exists():
        return WELCOME_GIF_PATH
    return None


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
    global _WELCOME_FILE_ID
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
    media_path = get_welcome_media_path()

    if _WELCOME_FILE_ID:
        try:
            await message.answer_animation(
                _WELCOME_FILE_ID,
                caption=text,
                reply_markup=main_menu(lang),
                parse_mode="HTML",
            )
            return
        except Exception:
            _WELCOME_FILE_ID = None

    if media_path:
        try:
            sent = await message.answer_animation(
                FSInputFile(str(media_path)),
                caption=text,
                reply_markup=main_menu(lang),
                parse_mode="HTML",
            )
            if sent and sent.animation:
                _WELCOME_FILE_ID = sent.animation.file_id
            elif sent and sent.document:
                _WELCOME_FILE_ID = sent.document.file_id
            return
        except Exception as e:
            logger.warning("Failed to send welcome animation: %s", e)
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
    """Save selected language and present animated main menu."""
    await users_service.set_language(session, user, callback_data.code)
    await session.commit()
    await query.answer()

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
    media_path = get_welcome_media_path()
    if media_path:
        await render_animation_step(
            query,
            media_path,
            text,
            reply_markup=main_menu(lang),
        )
    else:
        await render_menu_step(query, text, reply_markup=main_menu(lang))
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
            f"{icon_gift} <b>SEO Store Referral Program</b>\n\n"
            f"Invite friends and earn <b>{bonus}</b> to your balance "
            f"for every registered customer!\n\n"
            f"🔗 Your unique referral link:\n"
            f"<code>{link}</code>\n\n"
            f"<i>Bonus is credited immediately upon their first /start.</i>"
        )
    else:
        text = (
            f"{icon_gift} <b>Реферальна програма SEO Store</b>\n\n"
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
            f"{icon_gift} <b>Referral Program</b>\n\n"
            f"Share your link and get <b>{bonus}</b> for each friend:\n"
            f"<code>{link}</code>",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            f"{icon_gift} <b>Реферальна програма</b>\n\n"
            f"Діліться посиланням та отримуйте по <b>{bonus}</b> за кожного друга:\n"
            f"<code>{link}</code>",
            parse_mode="HTML",
        )
