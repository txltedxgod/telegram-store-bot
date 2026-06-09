"""Favorites: list and toggle."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import FavoriteCB, MenuCB
from bot.keyboards.user import back_home, favorites_kb
from bot.services import favorites as favorites_service

router = Router(name="favorites")


@router.callback_query(MenuCB.filter(F.action == "favorites"))
async def show_favorites(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    favorites = await favorites_service.list_favorites(session, user.id)
    if not favorites:
        await query.message.edit_text(
            "⭐ <b>Избранное</b>\n\nСписок пуст. Добавляйте товары из карточки товара.",
            reply_markup=back_home(),
        )
        await query.answer()
        return
    await query.message.edit_text(
        "⭐ <b>Избранное</b>\n\nВыберите товар:",
        reply_markup=favorites_kb(favorites),
    )
    await query.answer()


@router.callback_query(FavoriteCB.filter())
async def toggle_favorite(
    query: CallbackQuery, callback_data: FavoriteCB, session: AsyncSession, user: User
) -> None:
    now_fav = await favorites_service.toggle(session, user.id, callback_data.product_id)
    await query.answer(
        "Добавлено в избранное ⭐" if now_fav else "Удалено из избранного"
    )
