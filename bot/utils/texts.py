"""User-facing text builders with Ukrainian (default) and English localization,
clean layout (no long dashes), dual UAH/USD pricing, and custom emojis.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from bot.database.models import CartItem, Order, OrderStatus, Product, User
from bot.utils.emojis import (
    EMOJI_ARROW_DOWN,
    EMOJI_CALENDAR,
    EMOJI_CARD,
    EMOJI_CHART,
    EMOJI_CHECK,
    EMOJI_COIN,
    EMOJI_CROSS,
    EMOJI_ID,
    EMOJI_INFO,
    EMOJI_LANGUAGE,
    EMOJI_LIGHTNING,
    EMOJI_LOCK,
    EMOJI_MOBILE,
    EMOJI_MONEY,
    EMOJI_ORDERS,
    EMOJI_PENDING,
    EMOJI_PHONE,
    EMOJI_PROFILE,
    EMOJI_STAR,
    EMOJI_TAG,
    EMOJI_CHAT,
    EMOJI_UA,
    EMOJI_UK,
    EMOJI_WAVE,
    EMOJI_CART,
    ce,
)

# Exchange rate: 1 USD ~ 41.5 UAH
UAH_TO_USD_RATE = Decimal("41.5")

STATUS_LABELS_UK: dict[OrderStatus, str] = {
    OrderStatus.pending: f"{ce(EMOJI_PENDING, '⏳')} Очікує оплати",
    OrderStatus.paid: f"{ce(EMOJI_CARD, '💳')} Оплачено (в обробці)",
    OrderStatus.completed: f"{ce(EMOJI_CHECK, '✅')} Успішно виконано",
    OrderStatus.cancelled: f"{ce(EMOJI_CROSS, '❌')} Скасовано",
}

STATUS_LABELS_EN: dict[OrderStatus, str] = {
    OrderStatus.pending: f"{ce(EMOJI_PENDING, '⏳')} Pending Payment",
    OrderStatus.paid: f"{ce(EMOJI_CARD, '💳')} Paid (Processing)",
    OrderStatus.completed: f"{ce(EMOJI_CHECK, '✅')} Completed",
    OrderStatus.cancelled: f"{ce(EMOJI_CROSS, '❌')} Cancelled",
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
    icon_lightning = ce(EMOJI_LIGHTNING, "⚡️")
    icon_lang = ce(EMOJI_LANGUAGE, "🌐")
    return (
        f"{icon_lightning} <b>SEO Store</b>\n\n"
        f"{icon_lang} <b>Оберіть мову інтерфейсу:</b>\n"
        f"Please choose your preferred language below:"
    )


def welcome_text(user: User) -> str:
    lang = get_lang(user)
    name = user.full_name or ("customer" if lang == "en" else "покупець")
    icon_wave = ce(EMOJI_WAVE, "👋")
    icon_arrow = ce(EMOJI_ARROW_DOWN, "⬇️")
    icon_lightning = ce(EMOJI_LIGHTNING, "⚡️")
    icon_coin = ce(EMOJI_COIN, "🪙")
    icon_star = ce(EMOJI_STAR, "⭐️")
    icon_lock = ce(EMOJI_LOCK, "🔒")

    if lang == "en":
        return (
            f"{icon_lightning} <b>SEO Store</b>\n\n"
            f"{icon_wave} Welcome, <b>{name}</b>!\n\n"
            f"{icon_coin} Your balance: <b>{money(user.balance)}</b>\n"
            f"{icon_star} Catalog: <b>Telegram Premium, AI, VPN, Steam, Software</b>\n"
            f"{icon_lock} Instant 24/7 automated delivery\n\n"
            f"Choose a section from the menu below {icon_arrow}"
        )

    return (
        f"{icon_lightning} <b>SEO Store</b>\n\n"
        f"{icon_wave} Привіт, <b>{name}</b>!\n\n"
        f"{icon_coin} Ваш баланс: <b>{money(user.balance)}</b>\n"
        f"{icon_star} Каталог: <b>Telegram Premium, AI, VPN, Steam, Софт</b>\n"
        f"{icon_lock} Автоматична моментальна видача 24/7\n\n"
        f"Оберіть необхідний розділ у меню нижче {icon_arrow}"
    )


def product_card(product: Product, user: User | None = None) -> str:
    lang = get_lang(user)
    icon_lock = ce(EMOJI_LOCK, "🔒")
    icon_money = ce(EMOJI_MONEY, "💰")
    icon_box = ce(EMOJI_ORDERS, "📦")
    icon_info = ce(EMOJI_INFO, "⚠️")

    if lang == "en":
        stock_line = (
            f"In stock: <b>{product.stock} pcs.</b>"
            if product.in_stock
            else f"<b>{icon_info} Out of stock</b>"
        )
        return (
            f"<b>{product.name}</b>\n\n"
            f"{icon_money} Price: <b>{money(product.price)}</b>\n"
            f"{icon_box} {stock_line}\n\n"
            f"<b>Description:</b>\n"
            f"{product.description or '-'}\n\n"
            f"{icon_lock} <i>Quality guaranteed with automated instant delivery</i>"
        )

    stock_line = (
        f"В наявності: <b>{product.stock} шт.</b>"
        if product.in_stock
        else f"<b>{icon_info} Немає в наявності</b>"
    )
    return (
        f"<b>{product.name}</b>\n\n"
        f"{icon_money} Вартість: <b>{money(product.price)}</b>\n"
        f"{icon_box} {stock_line}\n\n"
        f"<b>Опис товару:</b>\n"
        f"{product.description or '-'}\n\n"
        f"{icon_lock} <i>Гарантія якості та автоматична видача</i>"
    )


def cart_text(items: Iterable[CartItem], total: Decimal, user: User | None = None) -> str:
    lang = get_lang(user)
    icon_cart = ce(EMOJI_CART, "🧺")

    if lang == "en":
        lines = [f"{icon_cart} <b>Shopping Cart</b>\n"]
        for item in items:
            subtotal = Decimal(item.product.price) * item.quantity
            clean_name = item.product.name.lstrip("⭐️⭐🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
            lines.append(
                f"• <b>{clean_name}</b>\n"
                f"  {item.quantity} pcs × {money(item.product.price)} = <b>{money(subtotal)}</b>"
            )
        lines.append(f"\nTotal to pay: <b>{money(total)}</b>")
        return "\n".join(lines)

    lines = [f"{icon_cart} <b>Кошик замовлень</b>\n"]
    for item in items:
        subtotal = Decimal(item.product.price) * item.quantity
        clean_name = item.product.name.lstrip("⭐️⭐🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
        lines.append(
            f"• <b>{clean_name}</b>\n"
            f"  {item.quantity} шт. × {money(item.product.price)} = <b>{money(subtotal)}</b>"
        )
    lines.append(f"\nРазом до сплати: <b>{money(total)}</b>")
    return "\n".join(lines)


def profile_text(user: User, orders_count: int, total_spent: Decimal) -> str:
    lang = get_lang(user)
    username = f"@{user.username}" if user.username else "-"
    icon_profile = ce(EMOJI_PROFILE, "👤")
    icon_id = ce(EMOJI_ID, "🆔")
    icon_mobile = ce(EMOJI_MOBILE, "📱")
    icon_lang = ce(EMOJI_LANGUAGE, "🌐")
    icon_cal = ce(EMOJI_CALENDAR, "📅")
    icon_coin = ce(EMOJI_COIN, "🪙")
    icon_box = ce(EMOJI_ORDERS, "📦")
    icon_money = ce(EMOJI_MONEY, "💸")
    flag_uk = ce(EMOJI_UA, "🇺🇦")
    flag_en = ce(EMOJI_UK, "🇬🇧")
    lang_str = f"{flag_uk} Українська" if user.language_code == "uk" else f"{flag_en} English"

    if lang == "en":
        return (
            f"{icon_profile} <b>Customer Profile</b>\n\n"
            f"{icon_id} Telegram ID: <code>{user.telegram_id}</code>\n"
            f"{icon_mobile} Username: {username}\n"
            f"{icon_lang} Language: <b>{lang_str}</b>\n"
            f"{icon_cal} Registered: {fmt_date(user.created_at)}\n\n"
            f"{icon_coin} Account Balance: <b>{money(user.balance)}</b>\n"
            f"{icon_box} Completed Orders: <b>{orders_count}</b>\n"
            f"{icon_money} Total Spent: <b>{money(total_spent)}</b>\n\n"
            f"<i>Top up your balance and earn bonuses by referring friends!</i>"
        )

    return (
        f"{icon_profile} <b>Особистий кабінет</b>\n\n"
        f"{icon_id} Telegram ID: <code>{user.telegram_id}</code>\n"
        f"{icon_mobile} Юзернейм: {username}\n"
        f"{icon_lang} Мова: <b>{lang_str}</b>\n"
        f"{icon_cal} З нами з: {fmt_date(user.created_at)}\n\n"
        f"{icon_coin} Баланс рахунку: <b>{money(user.balance)}</b>\n"
        f"{icon_box} Оформлено замовлень: <b>{orders_count}</b>\n"
        f"{icon_money} Загальна сума покупок: <b>{money(total_spent)}</b>\n\n"
        f"<i>Поповнюйте баланс та отримуйте бонуси за запрошення друзів!</i>"
    )


def order_card(order: Order, user: User | None = None) -> str:
    lang = get_lang(user)
    icon_box = ce(EMOJI_ORDERS, "📦")
    icon_chart = ce(EMOJI_CHART, "📊")
    icon_cal = ce(EMOJI_CALENDAR, "📅")
    icon_tag = ce(EMOJI_TAG, "🏷")
    icon_card = ce(EMOJI_CARD, "💳")
    icon_phone = ce(EMOJI_PHONE, "📞")
    icon_chat = ce(EMOJI_CHAT, "💬")
    icon_star = ce(EMOJI_STAR, "⭐️")

    if lang == "en":
        lines = [
            f"{icon_box} <b>Order #{order.id}</b>\n",
            f"{icon_chart} Status: <b>{status_label(order.status, 'en')}</b>",
            f"{icon_cal} Date: {fmt_date(order.created_at)}\n",
        ]
        for item in order.items:
            clean_pname = item.product_name.lstrip("⭐️⭐🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
            lines.append(
                f"• {icon_star} <b>{clean_pname}</b> ×{item.quantity} • <b>{money(item.subtotal)}</b>"
            )
        if order.discount and Decimal(order.discount) > 0:
            lines.append(f"\n{icon_tag} Promo code discount: −{money(order.discount)}")
        lines.append(f"\nTotal: <b>{money(order.total_price)}</b>")
        if order.payment_method:
            lines.append(f"{icon_card} Payment method: <b>{order.payment_method}</b>")
        if order.contact:
            lines.append(f"{icon_phone} Contact: <code>{order.contact}</code>")
        if order.comment:
            lines.append(f"{icon_chat} Comment: {order.comment}")
        return "\n".join(lines)

    lines = [
        f"{icon_box} <b>Замовлення #{order.id}</b>\n",
        f"{icon_chart} Статус: <b>{status_label(order.status, 'uk')}</b>",
        f"{icon_cal} Дата: {fmt_date(order.created_at)}\n",
    ]
    for item in order.items:
        clean_pname = item.product_name.lstrip("⭐️⭐🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
        lines.append(
            f"• {icon_star} <b>{clean_pname}</b> ×{item.quantity} • <b>{money(item.subtotal)}</b>"
        )
    if order.discount and Decimal(order.discount) > 0:
        lines.append(f"\n{icon_tag} Знижка за промокодом: −{money(order.discount)}")
    lines.append(f"\nРазом: <b>{money(order.total_price)}</b>")
    if order.payment_method:
        lines.append(f"{icon_card} Спосіб оплати: <b>{order.payment_method}</b>")
    if order.contact:
        lines.append(f"{icon_phone} Контакт для зв'язку: <code>{order.contact}</code>")
    if order.comment:
        lines.append(f"{icon_chat} Коментар: {order.comment}")
    return "\n".join(lines)
