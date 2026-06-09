"""Order checkout flow (FSM): contact -> comment -> create order."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.models import User
from bot.keyboards.callbacks import CartCB, CheckoutCB
from bot.keyboards.user import (
    back_home,
    checkout_cancel_kb,
    checkout_comment_kb,
)
from bot.services import cart as cart_service
from bot.services import orders as orders_service
from bot.states import CheckoutSG
from bot.utils.logger import get_logger

logger = get_logger("bot.checkout")
router = Router(name="checkout")


@router.callback_query(CartCB.filter(F.action == "checkout"))
async def start_checkout(
    query: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    items = await cart_service.get_items(session, user.id)
    if not items:
        await query.answer("Корзина пуста", show_alert=True)
        return
    await state.set_state(CheckoutSG.contact)
    await query.message.edit_text(
        "📝 <b>Оформление заказа</b>\n\n"
        "Шаг 1/2. Введите ваш Telegram (@username) или телефон для связи:",
        reply_markup=checkout_cancel_kb(),
    )
    await query.answer()


@router.callback_query(CheckoutCB.filter(F.action == "cancel"))
async def cancel_checkout(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.edit_text(
        "Оформление отменено.", reply_markup=back_home()
    )
    await query.answer()


@router.message(CheckoutSG.contact, F.text)
async def checkout_contact(message: Message, state: FSMContext) -> None:
    await state.update_data(contact=message.text.strip())
    await state.set_state(CheckoutSG.comment)
    await message.answer(
        "Шаг 2/2. Добавьте комментарий к заказу или пропустите шаг:",
        reply_markup=checkout_comment_kb(),
    )


async def _finalize(
    message: Message, session: AsyncSession, user: User, state: FSMContext, comment: str | None
) -> None:
    data = await state.get_data()
    await state.clear()
    try:
        order = await orders_service.create_from_cart(
            session,
            user_id=user.id,
            contact=data.get("contact"),
            comment=comment,
        )
    except orders_service.CheckoutError as exc:
        await message.answer(f"⚠ {exc}", reply_markup=back_home())
        return

    logger.info("User %s created order #%s", user.telegram_id, order.id)
    await message.answer(
        "✅ <b>Заказ успешно создан!</b>\n\n"
        f"Номер заказа: <b>#{order.id}</b>\n"
        "Статус: ⭐ Ожидает оплаты\n\n"
        "Мы свяжемся с вами в ближайшее время.",
        reply_markup=back_home(),
    )
    await _notify_admins_new_order(message, order.id, user)


@router.message(CheckoutSG.comment, F.text)
async def checkout_comment(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _finalize(message, session, user, state, message.text.strip())


@router.callback_query(CheckoutCB.filter(F.action == "skip"), CheckoutSG.comment)
async def checkout_skip_comment(
    query: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _finalize(query.message, session, user, state, None)
    await query.answer()


async def _notify_admins_new_order(message: Message, order_id: int, user: User) -> None:
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                f"🔔 Новый заказ <b>#{order_id}</b> от "
                f"{('@' + user.username) if user.username else user.telegram_id}",
            )
        except Exception:  # noqa: BLE001 - best effort notification
            continue
