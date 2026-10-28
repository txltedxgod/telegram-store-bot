"""User-facing text builders and formatting helpers (Russian locale)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from bot.config import settings
from bot.database.models import CartItem, Order, OrderStatus, Product, User

STATUS_LABELS: dict[OrderStatus, str] = {
    OrderStatus.pending: "⏳ Ожидает оплаты",
    OrderStatus.paid: "💳 Оплачен (в обработке)",
    OrderStatus.completed: "✅ Успешно выполнен",
    OrderStatus.cancelled: "❌ Отменён",
}


def money(value: Decimal | int | float | None) -> str:
    """Format a monetary value like '12 500 ₽'."""
    amount = Decimal(str(value or 0))
    whole = int(amount.to_integral_value())
    formatted = f"{whole:,}".replace(",", "\u202f")
    return f"{formatted} {settings.currency}"


def status_label(status: OrderStatus) -> str:
    return STATUS_LABELS.get(status, str(status))


def fmt_date(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.strftime("%d.%m.%Y в %H:%M")


def welcome_text(user: User) -> str:
    name = user.full_name or "покупатель"
    return (
        f"⚡️ <b>SEO STORE • Цифровой Маркетплейс</b>\n"
        f"────────────────────────\n"
        f"👋 Привет, <b>{name}</b>!\n\n"
        f"💳 Ваш баланс: <b>{money(user.balance)}</b>\n"
        f"💎 Каталог: <b>Telegram Premium, AI, VPN, Steam, Soft</b>\n"
        f"🔒 Моментальная автоматическая выдача 24/7\n"
        f"────────────────────────\n"
        f"Выберите интересующий раздел в меню ниже ⬇️"
    )


def product_card(product: Product) -> str:
    stock_line = (
        f"В наличии: <b>{product.stock} шт.</b>"
        if product.in_stock
        else "<b>⚠️ Нет в наличии</b>"
    )
    description = product.description or "—"
    return (
        f"<b>{product.name}</b>\n"
        f"────────────────────────\n"
        f"💰 Стоимость: <b>{money(product.price)}</b>\n"
        f"📦 {stock_line}\n\n"
        f"<b>Описание товара:</b>\n"
        f"{description}\n"
        f"────────────────────────\n"
        f"🔒 <i>Гарантия качества и автоматическая выдача</i>"
    )


def cart_text(items: Iterable[CartItem], total: Decimal) -> str:
    lines = [
        "🧺 <b>Ваша корзина покупок</b>\n"
        "────────────────────────"
    ]
    for item in items:
        subtotal = Decimal(item.product.price) * item.quantity
        lines.append(
            f"• <b>{item.product.name}</b>\n"
            f"  {item.quantity} шт. × {money(item.product.price)} = <b>{money(subtotal)}</b>"
        )
    lines.append("────────────────────────")
    lines.append(f"Итого к оплате: <b>{money(total)}</b>")
    return "\n".join(lines)


def profile_text(user: User, orders_count: int, total_spent: Decimal) -> str:
    username = f"@{user.username}" if user.username else "—"
    return (
        "👤 <b>Личный кабинет</b>\n"
        "────────────────────────\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"📱 Никнейм: {username}\n"
        f"📅 С нами с: {fmt_date(user.created_at)}\n\n"
        f"💳 Баланс счёта: <b>{money(user.balance)}</b>\n"
        f"📦 Оформлено заказов: <b>{orders_count}</b>\n"
        f"💸 Всего покупок на: <b>{money(total_spent)}</b>\n"
        "────────────────────────\n"
        "<i>Пополняйте баланс и получайте бонусы за приглашение друзей!</i>"
    )


def order_card(order: Order) -> str:
    lines = [
        f"📦 <b>Заказ #{order.id}</b>\n"
        f"────────────────────────\n",
        f"📊 Статус: <b>{status_label(order.status)}</b>",
        f"📅 Дата: {fmt_date(order.created_at)}\n",
    ]
    for item in order.items:
        lines.append(
            f"• {item.product_name} ×{item.quantity} — <b>{money(item.subtotal)}</b>"
        )
    if order.discount and Decimal(order.discount) > 0:
        lines.append(f"\n🏷 Скидка по промокоду: −{money(order.discount)}")
    lines.append("\n────────────────────────")
    lines.append(f"Итого: <b>{money(order.total_price)}</b>")
    if order.contact:
        lines.append(f"\n📞 Контакт для связи: <code>{order.contact}</code>")
    if order.comment:
        lines.append(f"💬 Комментарий: {order.comment}")
    return "\n".join(lines)
