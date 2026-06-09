"""User-facing text builders and formatting helpers (Russian locale)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from bot.config import settings
from bot.database.models import CartItem, Order, OrderStatus, Product, User

STATUS_LABELS: dict[OrderStatus, str] = {
    OrderStatus.pending: "⭐ Ожидает оплаты",
    OrderStatus.paid: "💳 Оплачен",
    OrderStatus.completed: "✅ Выполнен",
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
    return value.strftime("%d.%m.%Y")


def welcome_text(user: User) -> str:
    return (
        "👋 <b>Добро пожаловать!</b>\n\n"
        f"Ваш баланс: <b>{money(user.balance)}</b>\n\n"
        "Выберите действие:"
    )


def product_card(product: Product) -> str:
    stock_line = (
        f"В наличии: <b>{product.stock}</b>"
        if product.in_stock
        else "<b>Нет в наличии</b>"
    )
    description = product.description or "—"
    return (
        f"<b>{product.name}</b>\n\n"
        f"💰 Цена: <b>{money(product.price)}</b>\n"
        f"📦 {stock_line}\n\n"
        f"{description}"
    )


def cart_text(items: Iterable[CartItem], total: Decimal) -> str:
    lines = ["🧺 <b>Корзина</b>\n"]
    for item in items:
        subtotal = Decimal(item.product.price) * item.quantity
        lines.append(
            f"• {item.product.name} ×{item.quantity} — <b>{money(subtotal)}</b>"
        )
    lines.append("\n————————————————")
    lines.append(f"Итого: <b>{money(total)}</b>")
    return "\n".join(lines)


def profile_text(user: User, orders_count: int, total_spent: Decimal) -> str:
    username = f"@{user.username}" if user.username else "—"
    return (
        "👤 <b>Ваш профиль</b>\n\n"
        f"ID: <code>{user.telegram_id}</code>\n"
        f"Username: {username}\n"
        f"Дата регистрации: {fmt_date(user.created_at)}\n\n"
        f"💳 Баланс: <b>{money(user.balance)}</b>\n"
        f"📦 Заказов: <b>{orders_count}</b>\n"
        f"💸 Потрачено: <b>{money(total_spent)}</b>"
    )


def order_card(order: Order) -> str:
    lines = [
        f"📦 <b>Заказ #{order.id}</b>\n",
        f"Статус: {status_label(order.status)}",
        f"Дата: {fmt_date(order.created_at)}\n",
    ]
    for item in order.items:
        lines.append(
            f"• {item.product_name} ×{item.quantity} — {money(item.subtotal)}"
        )
    if order.discount and Decimal(order.discount) > 0:
        lines.append(f"\n🏷 Скидка: −{money(order.discount)}")
    lines.append("\n————————————————")
    lines.append(f"Итого: <b>{money(order.total_price)}</b>")
    if order.contact:
        lines.append(f"\n📞 Контакт: {order.contact}")
    if order.comment:
        lines.append(f"💬 Комментарий: {order.comment}")
    return "\n".join(lines)
