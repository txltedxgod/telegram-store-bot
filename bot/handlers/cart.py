"""Cart view and item management with multi-language support."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import CartCB, MenuCB
from bot.keyboards.user import back_home, cart_kb
from bot.services import cart as cart_service
from bot.utils.texts import cart_text, get_lang
from bot.utils.ui import render_menu_step

router = Router(name="cart")


async def _render_cart(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = get_lang(user)
    items = await cart_service.get_items(session, user.id)
    if not items:
        empty_text = (
            "🧺 <b>Your shopping cart is empty</b>\n\nBrowse the catalog to add items."
            if lang == "en"
            else "🧺 <b>Ваш кошик порожній</b>\n\nДодайте товари з каталогу."
        )
        await render_menu_step(query, empty_text, reply_markup=back_home(lang))
        return
    total = cart_service.total(items)
    await render_menu_step(
        query,
        cart_text(items, total, user),
        reply_markup=cart_kb(items, lang=lang),
    )


@router.callback_query(MenuCB.filter(F.action == "cart"))
async def show_cart(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    await _render_cart(query, session, user)
    await query.answer()


@router.callback_query(CartCB.filter(F.action == "noop"))
async def noop(query: CallbackQuery) -> None:
    await query.answer()


@router.callback_query(CartCB.filter(F.action.in_(["inc", "dec"])))
async def change_qty(
    query: CallbackQuery, callback_data: CartCB, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    item = await cart_service.get_item(session, user.id, callback_data.product_id)
    if item is None:
        await query.answer()
        await _render_cart(query, session, user)
        return
    delta = 1 if callback_data.action == "inc" else -1
    if delta > 0 and item.quantity >= item.product.stock:
        alert = "Maximum available stock reached" if lang == "en" else "Більше немає на складі"
        await query.answer(alert, show_alert=True)
        return
    await cart_service.change_quantity(session, item, delta)
    await _render_cart(query, session, user)
    await query.answer()


@router.callback_query(CartCB.filter(F.action == "remove"))
async def remove_item(
    query: CallbackQuery, callback_data: CartCB, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    await cart_service.remove_item(session, user.id, callback_data.product_id)
    alert = "Item removed" if lang == "en" else "Товар видалено"
    await query.answer(alert)
    await _render_cart(query, session, user)


@router.callback_query(CartCB.filter(F.action == "clear"))
async def clear_cart(
    query: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    await cart_service.clear(session, user.id)
    alert = "Cart cleared" if lang == "en" else "Кошик очищено"
    await query.answer(alert)
    await _render_cart(query, session, user)
