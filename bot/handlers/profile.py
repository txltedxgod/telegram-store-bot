"""User profile."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import MenuCB
from bot.keyboards.user import back_home
from bot.services import users as users_service
from bot.utils.texts import profile_text

router = Router(name="profile")


@router.callback_query(MenuCB.filter(F.action == "profile"))
async def show_profile(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    orders_count, total_spent = await users_service.user_order_stats(session, user.id)
    await query.message.edit_text(
        profile_text(user, orders_count, total_spent),
        reply_markup=back_home(),
    )
    await query.answer()
