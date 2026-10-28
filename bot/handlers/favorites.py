"""Favorites: list and toggle with localization."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import FavoriteCB, MenuCB
from bot.keyboards.user import back_home, favorites_kb
from bot.services import favorites as favorites_service
from bot.utils.emojis import EMOJI_STAR, ce
from bot.utils.texts import get_lang
from bot.utils.ui import render_menu_step

router = Router(name="favorites")


@router.callback_query(MenuCB.filter(F.action == "favorites"))
async def show_favorites(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = get_lang(user)
    favorites = await favorites_service.list_favorites(session, user.id)
    icon_star = ce(EMOJI_STAR, "⭐️")
    if not favorites:
        empty_text = (
            f"{icon_star} <b>Favorites</b>\n\nYour favorites list is empty. Add items from product cards."
            if lang == "en"
            else f"{icon_star} <b>Обране</b>\n\nСписок порожній. Додавайте товари з карток товарів."
        )
        await render_menu_step(query, empty_text, reply_markup=back_home(lang))
        await query.answer()
        return

    prompt = (
        f"{icon_star} <b>Favorites</b>\n\nSelect an item:"
        if lang == "en"
        else f"{icon_star} <b>Обране</b>\n\nОберіть товар:"
    )
    await render_menu_step(
        query,
        prompt,
        reply_markup=favorites_kb(favorites, lang=lang),
    )
    await query.answer()


@router.callback_query(FavoriteCB.filter())
async def toggle_favorite(
    query: CallbackQuery, callback_data: FavoriteCB, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    now_fav = await favorites_service.toggle(session, user.id, callback_data.product_id)
    if lang == "en":
        alert = "Added to favorites ⭐" if now_fav else "Removed from favorites"
    else:
        alert = "Додано до обраного ⭐" if now_fav else "Прибрано з обраного"
    await query.answer(alert)
