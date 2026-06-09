"""My orders: list and detail (purchase history)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import MenuCB, OrderCB
from bot.keyboards.user import back_home, order_detail_kb, orders_kb
from bot.services import orders as orders_service
from bot.utils.texts import order_card

router = Router(name="orders")


@router.callback_query(MenuCB.filter(F.action == "orders"))
async def show_orders(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    orders = await orders_service.list_user_orders(session, user.id)
    if not orders:
        await query.message.edit_text(
            "📦 <b>Мои заказы</b>\n\nУ вас пока нет заказов.",
            reply_markup=back_home(),
        )
        await query.answer()
        return
    await query.message.edit_text(
        "📦 <b>Мои заказы</b>\n\nВыберите заказ:",
        reply_markup=orders_kb(orders),
    )
    await query.answer()


@router.callback_query(OrderCB.filter())
async def show_order(
    query: CallbackQuery, callback_data: OrderCB, session: AsyncSession, user: User
) -> None:
    order = await orders_service.get_order(session, callback_data.order_id)
    if order is None or order.user_id != user.id:
        await query.answer("Заказ не найден", show_alert=True)
        return
    await query.message.edit_text(order_card(order), reply_markup=order_detail_kb())
    await query.answer()
