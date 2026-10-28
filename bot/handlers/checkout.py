"""Order checkout flow (FSM) with payment method selection (Card UAH / Crypto) and localization."""
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
    payment_methods_kb,
)
from bot.services import cart as cart_service
from bot.services import orders as orders_service
from bot.states import CheckoutSG
from bot.utils.emojis import EMOJI_CHECK, EMOJI_COIN, EMOJI_LOCK, ce
from bot.utils.logger import get_logger
from bot.utils.texts import get_lang, money

logger = get_logger("bot.checkout")
router = Router(name="checkout")


@router.callback_query(CartCB.filter(F.action == "checkout"))
async def start_checkout(
    query: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = get_lang(user)
    items = await cart_service.get_items(session, user.id)
    if not items:
        empty = "Your cart is empty" if lang == "en" else "Кошик порожній"
        await query.answer(empty, show_alert=True)
        return

    await query.answer()
    await state.set_state(CheckoutSG.payment_method)
    if lang == "en":
        text = (
            "💳 <b>Checkout • Step 1/3</b>\n\n"
            "Please select your payment method:"
        )
    else:
        text = (
            "💳 <b>Оформлення замовлення • Крок 1/3</b>\n\n"
            "Оберіть зручний спосіб оплати:"
        )

    await query.message.edit_text(text, reply_markup=payment_methods_kb(lang), parse_mode="HTML")


@router.callback_query(CheckoutCB.filter(F.action == "pay_method"), CheckoutSG.payment_method)
async def select_payment_method(
    query: CallbackQuery, callback_data: CheckoutCB, state: FSMContext, user: User
) -> None:
    lang = get_lang(user)
    method = callback_data.method
    await state.update_data(payment_method=method)
    await state.set_state(CheckoutSG.contact)

    await query.answer()
    if lang == "en":
        text = (
            "📝 <b>Checkout • Step 2/3</b>\n\n"
            "Enter your Telegram (@username) or contact info for automated delivery:"
        )
    else:
        text = (
            "📝 <b>Оформлення замовлення • Крок 2/3</b>\n\n"
            "Введіть ваш Telegram (@username) або контакт для автоматичної видачі товару:"
        )

    await query.message.edit_text(text, reply_markup=checkout_cancel_kb(lang), parse_mode="HTML")


@router.callback_query(CheckoutCB.filter(F.action == "cancel"))
async def cancel_checkout(query: CallbackQuery, state: FSMContext, user: User) -> None:
    await query.answer()
    lang = get_lang(user)
    await state.clear()
    text = "Checkout cancelled." if lang == "en" else "Оформлення скасовано."
    await query.message.edit_text(text, reply_markup=back_home(lang), parse_mode="HTML")


@router.message(CheckoutSG.contact, F.text)
async def checkout_contact(message: Message, state: FSMContext, user: User) -> None:
    lang = get_lang(user)
    await state.update_data(contact=message.text.strip())
    await state.set_state(CheckoutSG.comment)

    if lang == "en":
        text = (
            "💬 <b>Checkout • Step 3/3</b>\n\n"
            "Add a note/comment to your order, or press skip:"
        )
    else:
        text = (
            "💬 <b>Оформлення замовлення • Крок 3/3</b>\n\n"
            "Додайте коментар або примітку до замовлення (або пропустіть крок):"
        )

    await message.answer(text, reply_markup=checkout_comment_kb(lang), parse_mode="HTML")


async def _finalize(
    message: Message, session: AsyncSession, user: User, state: FSMContext, comment: str | None
) -> None:
    lang = get_lang(user)
    data = await state.get_data()
    payment_method = data.get("payment_method", "crypto")
    contact = data.get("contact")
    await state.clear()

    try:
        order = await orders_service.create_from_cart(
            session,
            user_id=user.id,
            contact=contact,
            comment=comment,
            payment_method=payment_method,
        )
    except orders_service.CheckoutError as exc:
        await message.answer(f"⚠ {exc}", reply_markup=back_home(lang), parse_mode="HTML")
        return

    logger.info("User %s created order #%s with method %s", user.telegram_id, order.id, payment_method)
    icon_check = ce(EMOJI_CHECK, "✅")
    icon_coin = ce(EMOJI_COIN, "🪙")
    icon_lock = ce(EMOJI_LOCK, "🔒")

    # Payment details display
    if payment_method == "card_uah":
        pay_title_uk = "Картка UAH (Monobank / ПриватБанк)"
        pay_title_en = "Card UAH (Monobank / PrivatBank)"
        pay_details = (
            "💳 <b>Реквізити для оплати:</b>\n"
            "• Картка: <code>4149 6293 8471 9928</code> (Monobank)\n"
            "• Призначення: <code>Замовлення #" + str(order.id) + "</code>\n"
            "• Отримувач: ФОП / SEO Store"
        ) if lang == "uk" else (
            "💳 <b>Payment Requisites:</b>\n"
            "• Card: <code>4149 6293 8471 9928</code> (Monobank)\n"
            "• Reference: <code>Order #" + str(order.id) + "</code>\n"
            "• Recipient: FOP / SEO Store"
        )
    else:
        pay_title_uk = "Криптовалюта (USDT / TON / BTC)"
        pay_title_en = "Crypto (USDT / TON / BTC)"
        pay_details = (
            "⚡️ <b>Крипто-гаманці для оплати:</b>\n"
            "• <b>USDT (TRC-20):</b> <code>TXLTedxGodStoreOfficialTrx20Address</code>\n"
            "• <b>TON:</b> <code>UQBWx9_SeoStoreOfficialTonAddress</code>\n"
            "• <b>BTC:</b> <code>bc1q9seostoredigitalcryptostore12345</code>"
        ) if lang == "uk" else (
            "⚡️ <b>Crypto Deposit Wallets:</b>\n"
            "• <b>USDT (TRC-20):</b> <code>TXLTedxGodStoreOfficialTrx20Address</code>\n"
            "• <b>TON:</b> <code>UQBWx9_SeoStoreOfficialTonAddress</code>\n"
            "• <b>BTC:</b> <code>bc1q9seostoredigitalcryptostore12345</code>"
        )

    if lang == "en":
        summary = (
            f"{icon_check} <b>Order #{order.id} Successfully Placed!</b>\n\n"
            f"💰 Amount to pay: <b>{money(order.total_price)}</b>\n"
            f"{icon_coin} Payment method: <b>{pay_title_en}</b>\n\n"
            f"{pay_details}\n\n"
            f"{icon_lock} <i>After payment is detected, your digital goods and licenses will be delivered immediately!</i>"
        )
    else:
        summary = (
            f"{icon_check} <b>Замовлення #{order.id} успішно створено!</b>\n\n"
            f"💰 Сума до сплати: <b>{money(order.total_price)}</b>\n"
            f"{icon_coin} Спосіб оплати: <b>{pay_title_uk}</b>\n\n"
            f"{pay_details}\n\n"
            f"{icon_lock} <i>Після підтвердження транзакції цифровий ключ або ліцензія надійде автоматично в цей діалог!</i>"
        )

    await message.answer(summary, reply_markup=back_home(lang), parse_mode="HTML")
    await _notify_admins_new_order(message, order.id, user, payment_method)


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


async def _notify_admins_new_order(
    message: Message, order_id: int, user: User, method: str
) -> None:
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                f"🔔 Новий заказ <b>#{order_id}</b> ({method}) від "
                f"{('@' + user.username) if user.username else user.telegram_id}",
                parse_mode="HTML",
            )
        except Exception:
            continue
