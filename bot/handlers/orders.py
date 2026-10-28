"""My orders: list and detail (purchase history) with localization."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import MenuCB, OrderCB
from bot.keyboards.user import back_home, order_detail_kb, orders_kb
from bot.services import orders as orders_service
from bot.utils.texts import get_lang, order_card
from bot.utils.ui import render_menu_step

router = Router(name="orders")


@router.callback_query(MenuCB.filter(F.action == "orders"))
async def show_orders(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = get_lang(user)
    orders = await orders_service.list_user_orders(session, user.id)
    if not orders:
        empty_text = (
            "📦 <b>My Orders</b>\n\nYou have no orders yet."
            if lang == "en"
            else "📦 <b>Мої замовлення</b>\n\nУ вас поки немає замовлень."
        )
        await render_menu_step(query, empty_text, reply_markup=back_home(lang))
        await query.answer()
        return

    prompt = (
        "📦 <b>My Orders</b>\n\nSelect an order to view details:"
        if lang == "en"
        else "📦 <b>Мої замовлення</b>\n\nОберіть замовлення для перегляду деталей:"
    )
    await render_menu_step(
        query,
        prompt,
        reply_markup=orders_kb(orders, lang=lang),
    )
    await query.answer()


@router.callback_query(OrderCB.filter())
async def show_order(
    query: CallbackQuery, callback_data: OrderCB, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    order = await orders_service.get_order(session, callback_data.order_id)
    if order is None or order.user_id != user.id:
        not_found = "Order not found" if lang == "en" else "Замовлення не знайдено"
        await query.answer(not_found, show_alert=True)
        return
    await render_menu_step(
        query,
        order_card(order, user),
        reply_markup=order_detail_kb(lang),
    )
    await query.answer()
