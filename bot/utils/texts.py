"""User-facing text builders with Ukrainian (default) and English localization,
clean layout (no long dashes), dual UAH/USD pricing, and custom emojis.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from bot.database.models import CartItem, Order, OrderStatus, Product, User
from bot.utils.emojis import (
    EMOJI_CHECK,
    EMOJI_COIN,
    EMOJI_GIFT,
    EMOJI_LIGHTNING,
    EMOJI_LOCK,
    EMOJI_PROFILE,
    EMOJI_ROBOT,
    EMOJI_STAR,
    EMOJI_STORE,
    ce,
)

# Exchange rate: 1 USD ~ 41.5 UAH
UAH_TO_USD_RATE = Decimal("41.5")

STATUS_LABELS_UK: dict[OrderStatus, str] = {
    OrderStatus.pending: "⏳ Очікує оплати",
    OrderStatus.paid: "💳 Оплачено (в обробці)",
    OrderStatus.completed: "✅ Успішно виконано",
    OrderStatus.cancelled: "❌ Скасовано",
}

STATUS_LABELS_EN: dict[OrderStatus, str] = {
    OrderStatus.pending: "⏳ Pending Payment",
    OrderStatus.paid: "💳 Paid (Processing)",
    OrderStatus.completed: "✅ Completed",
    OrderStatus.cancelled: "❌ Cancelled",
}


def get_lang(user: User | None) -> str:
    if user and getattr(user, "language_code", None) in ("uk", "en"):
        return user.language_code
    return "uk"


def money(value: Decimal | int | float | None) -> str:
    """Format price in UAH (₴) and USD ($), e.g. '1 150 ₴ ($27.71)'."""
    uah = Decimal(str(value or 0))
    whole = int(uah.to_integral_value())
    formatted_uah = f"{whole:,}".replace(",", "\u202f")
    usd = (uah / UAH_TO_USD_RATE).quantize(Decimal("0.01"))
    return f"{formatted_uah} ₴ (${usd:.2f})"


def status_label(status: OrderStatus, lang: str = "uk") -> str:
    labels = STATUS_LABELS_EN if lang == "en" else STATUS_LABELS_UK
    return labels.get(status, str(status))


def fmt_date(value: datetime | None) -> str:
    if not value:
        return "-"
    return value.strftime("%d.%m.%Y %H:%M")


def language_prompt_text() -> str:
    return (
        f"{ce(EMOJI_LIGHTNING, '⚡️')} <b>SEO Store</b>\n\n"
        f"🌐 <b>Оберіть мову інтерфейсу:</b>\n"
        f"Please choose your preferred language below:"
    )


def welcome_text(user: User) -> str:
    lang = get_lang(user)
    name = user.full_name or ("customer" if lang == "en" else "покупець")
    icon_lightning = ce(EMOJI_LIGHTNING, "⚡️")
    icon_coin = ce(EMOJI_COIN, "🪙")
    icon_star = ce(EMOJI_STAR, "💎")
    icon_lock = ce(EMOJI_LOCK, "🔒")

    if lang == "en":
        return (
            f"{icon_lightning} <b>SEO Store</b>\n\n"
            f"👋 Welcome, <b>{name}</b>!\n\n"
            f"{icon_coin} Your balance: <b>{money(user.balance)}</b>\n"
            f"{icon_star} Catalog: <b>Telegram Premium, AI, VPN, Steam, Software</b>\n"
            f"{icon_lock} Instant 24/7 automated delivery\n\n"
            f"Choose a section from the menu below ⬇️"
        )

    return (
        f"{icon_lightning} <b>SEO Store</b>\n\n"
        f"👋 Привіт, <b>{name}</b>!\n\n"
        f"{icon_coin} Ваш баланс: <b>{money(user.balance)}</b>\n"
        f"{icon_star} Каталог: <b>Telegram Premium, AI, VPN, Steam, Софт</b>\n"
        f"{icon_lock} Автоматична моментальна видача 24/7\n\n"
        f"Оберіть необхідний розділ у меню нижче ⬇️"
    )


def product_card(product: Product, user: User | None = None) -> str:
    lang = get_lang(user)
    icon_lock = ce(EMOJI_LOCK, "🔒")

    if lang == "en":
        stock_line = (
            f"In stock: <b>{product.stock} pcs.</b>"
            if product.in_stock
            else "<b>⚠️ Out of stock</b>"
        )
        return (
            f"<b>{product.name}</b>\n\n"
            f"💰 Price: <b>{money(product.price)}</b>\n"
            f"📦 {stock_line}\n\n"
            f"<b>Description:</b>\n"
            f"{product.description or '-'}\n\n"
            f"{icon_lock} <i>Quality guaranteed with automated instant delivery</i>"
        )

    stock_line = (
        f"В наявності: <b>{product.stock} шт.</b>"
        if product.in_stock
        else "<b>⚠️ Немає в наявності</b>"
    )
    return (
        f"<b>{product.name}</b>\n\n"
        f"💰 Вартість: <b>{money(product.price)}</b>\n"
        f"📦 {stock_line}\n\n"
        f"<b>Опис товару:</b>\n"
        f"{product.description or '-'}\n\n"
        f"{icon_lock} <i>Гарантія якості та автоматична видача</i>"
    )


def cart_text(items: Iterable[CartItem], total: Decimal, user: User | None = None) -> str:
    lang = get_lang(user)
    if lang == "en":
        lines = ["🧺 <b>Shopping Cart</b>\n"]
        for item in items:
            subtotal = Decimal(item.product.price) * item.quantity
            lines.append(
                f"• <b>{item.product.name}</b>\n"
                f"  {item.quantity} pcs × {money(item.product.price)} = <b>{money(subtotal)}</b>"
            )
        lines.append(f"\nTotal to pay: <b>{money(total)}</b>")
        return "\n".join(lines)

    lines = ["🧺 <b>Кошик замовлень</b>\n"]
    for item in items:
        subtotal = Decimal(item.product.price) * item.quantity
        lines.append(
            f"• <b>{item.product.name}</b>\n"
            f"  {item.quantity} шт. × {money(item.product.price)} = <b>{money(subtotal)}</b>"
        )
    lines.append(f"\nРазом до сплати: <b>{money(total)}</b>")
    return "\n".join(lines)


def profile_text(user: User, orders_count: int, total_spent: Decimal) -> str:
    lang = get_lang(user)
    username = f"@{user.username}" if user.username else "-"
    icon_profile = ce(EMOJI_PROFILE, "👤")
    icon_coin = ce(EMOJI_COIN, "🪙")

    if lang == "en":
        return (
            f"{icon_profile} <b>Customer Profile</b>\n\n"
            f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
            f"📱 Username: {username}\n"
            f"🌐 Language: <b>{'🇺🇦 Українська' if user.language_code == 'uk' else '🇬🇧 English'}</b>\n"
            f"📅 Registered: {fmt_date(user.created_at)}\n\n"
            f"{icon_coin} Account Balance: <b>{money(user.balance)}</b>\n"
            f"📦 Completed Orders: <b>{orders_count}</b>\n"
            f"💸 Total Spent: <b>{money(total_spent)}</b>\n\n"
            f"<i>Top up your balance and earn bonuses by referring friends!</i>"
        )

    return (
        f"{icon_profile} <b>Особистий кабінет</b>\n\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"📱 Юзернейм: {username}\n"
        f"🌐 Мова: <b>{'🇺🇦 Українська' if user.language_code == 'uk' else '🇬🇧 English'}</b>\n"
        f"📅 З нами з: {fmt_date(user.created_at)}\n\n"
        f"{icon_coin} Баланс рахунку: <b>{money(user.balance)}</b>\n"
        f"📦 Оформлено замовлень: <b>{orders_count}</b>\n"
        f"💸 Загальна сума покупок: <b>{money(total_spent)}</b>\n\n"
        f"<i>Поповнюйте баланс та отримуйте бонуси за запрошення друзів!</i>"
    )


def order_card(order: Order, user: User | None = None) -> str:
    lang = get_lang(user)
    if lang == "en":
        lines = [
            f"📦 <b>Order #{order.id}</b>\n",
            f"📊 Status: <b>{status_label(order.status, 'en')}</b>",
            f"📅 Date: {fmt_date(order.created_at)}\n",
        ]
        for item in order.items:
            lines.append(
                f"• {item.product_name} ×{item.quantity} • <b>{money(item.subtotal)}</b>"
            )
        if order.discount and Decimal(order.discount) > 0:
            lines.append(f"\n🏷 Promo code discount: −{money(order.discount)}")
        lines.append(f"\nTotal: <b>{money(order.total_price)}</b>")
        if order.payment_method:
            lines.append(f"💳 Payment method: <b>{order.payment_method}</b>")
        if order.contact:
            lines.append(f"📞 Contact: <code>{order.contact}</code>")
        if order.comment:
            lines.append(f"💬 Comment: {order.comment}")
        return "\n".join(lines)

    lines = [
        f"📦 <b>Замовлення #{order.id}</b>\n",
        f"📊 Статус: <b>{status_label(order.status, 'uk')}</b>",
        f"📅 Дата: {fmt_date(order.created_at)}\n",
    ]
    for item in order.items:
        lines.append(
            f"• {item.product_name} ×{item.quantity} • <b>{money(item.subtotal)}</b>"
        )
    if order.discount and Decimal(order.discount) > 0:
        lines.append(f"\n🏷 Знижка за промокодом: −{money(order.discount)}")
    lines.append(f"\nРазом: <b>{money(order.total_price)}</b>")
    if order.payment_method:
        lines.append(f"💳 Спосіб оплати: <b>{order.payment_method}</b>")
    if order.contact:
        lines.append(f"📞 Контакт для зв'язку: <code>{order.contact}</code>")
    if order.comment:
        lines.append(f"💬 Коментар: {order.comment}")
    return "\n".join(lines)
