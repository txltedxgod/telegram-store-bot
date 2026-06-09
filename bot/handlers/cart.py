"""Cart view and item management."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import CartCB, MenuCB
from bot.keyboards.user import back_home, cart_kb
from bot.services import cart as cart_service
from bot.utils.texts import cart_text

router = Router(name="cart")

EMPTY_CART = "🧺 <b>Корзина пуста</b>\n\nДобавьте товары из каталога."


async def _render_cart(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    items = await cart_service.get_items(session, user.id)
    if not items:
        await query.message.edit_text(EMPTY_CART, reply_markup=back_home())
        return
    total = cart_service.total(items)
    await query.message.edit_text(cart_text(items, total), reply_markup=cart_kb(items))


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
    item = await cart_service.get_item(session, user.id, callback_data.product_id)
    if item is None:
        await query.answer()
        await _render_cart(query, session, user)
        return
    delta = 1 if callback_data.action == "inc" else -1
    if delta > 0 and item.quantity >= item.product.stock:
        await query.answer("Больше нет на складе", show_alert=True)
        return
    await cart_service.change_quantity(session, item, delta)
    await _render_cart(query, session, user)
    await query.answer()


@router.callback_query(CartCB.filter(F.action == "remove"))
async def remove_item(
    query: CallbackQuery, callback_data: CartCB, session: AsyncSession, user: User
) -> None:
    await cart_service.remove_item(session, user.id, callback_data.product_id)
    await _render_cart(query, session, user)
    await query.answer("Товар удалён")


@router.callback_query(CartCB.filter(F.action == "clear"))
async def clear_cart(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    await cart_service.clear(session, user.id)
    await query.message.edit_text(EMPTY_CART, reply_markup=back_home())
    await query.answer("Корзина очищена")
