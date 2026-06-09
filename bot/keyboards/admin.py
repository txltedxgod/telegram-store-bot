"""Inline keyboards for the admin panel."""
from __future__ import annotations

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Category, Order, OrderStatus, Product
from bot.keyboards.callbacks import AdminCB
from bot.utils.texts import money, status_label


def admin_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить товар", callback_data=AdminCB(action="add"), style=ButtonStyle.SUCCESS)
    kb.button(text="✏️ Изменить товар", callback_data=AdminCB(action="edit"), style=ButtonStyle.PRIMARY)
    kb.button(text="❌ Удалить товар", callback_data=AdminCB(action="delete"), style=ButtonStyle.DANGER)
    kb.button(text="📦 Заказы", callback_data=AdminCB(action="orders"))
    kb.button(text="📊 Статистика", callback_data=AdminCB(action="stats"))
    kb.button(text="📢 Рассылка", callback_data=AdminCB(action="broadcast"))
    kb.button(text="🏷 Промокоды", callback_data=AdminCB(action="promo"))
    kb.button(text="🏆 Топ товаров", callback_data=AdminCB(action="top"))
    kb.button(text="📄 Экспорт CSV", callback_data=AdminCB(action="export"))
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()


def back_admin() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="« В админ-панель", callback_data=AdminCB(action="menu"))
    return kb.as_markup()


def categories_pick_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(
            text=category.title,
            callback_data=AdminCB(action="pickcat", item_id=category.id),
        )
    kb.adjust(1)
    return kb.as_markup()


def products_pick_kb(products: list[Product], action: str) -> InlineKeyboardMarkup:
    """action = 'del' or 'editpick'."""
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(
            text=f"{product.name} ({money(product.price)}, ост. {product.stock})",
            callback_data=AdminCB(action=action, item_id=product.id),
            style=ButtonStyle.DANGER if action == "del" else None,
        )
    kb.button(text="« В админ-панель", callback_data=AdminCB(action="menu"))
    kb.adjust(1)
    return kb.as_markup()


def edit_field_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Название", callback_data=AdminCB(action="editfield", item_id=product_id, value="name"))
    kb.button(text="Цена", callback_data=AdminCB(action="editfield", item_id=product_id, value="price"))
    kb.button(text="Описание", callback_data=AdminCB(action="editfield", item_id=product_id, value="description"))
    kb.button(text="Остаток", callback_data=AdminCB(action="editfield", item_id=product_id, value="stock"))
    kb.button(text="« В админ-панель", callback_data=AdminCB(action="menu"))
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def admin_order_kb(order: Order) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for status in OrderStatus:
        if status == order.status:
            continue
        kb.button(
            text=f"→ {status_label(status)}",
            callback_data=AdminCB(action="setstatus", item_id=order.id, value=status.value),
            style=(
                ButtonStyle.DANGER
                if status == OrderStatus.cancelled
                else ButtonStyle.SUCCESS
                if status in (OrderStatus.paid, OrderStatus.completed)
                else None
            ),
        )
    kb.button(text="« К заказам", callback_data=AdminCB(action="orders"))
    kb.adjust(1)
    return kb.as_markup()


def admin_orders_kb(orders: list[Order]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for order in orders:
        kb.button(
            text=f"#{order.id} — {money(order.total_price)} — {status_label(order.status)}",
            callback_data=AdminCB(action="order", item_id=order.id),
        )
    kb.button(text="« В админ-панель", callback_data=AdminCB(action="menu"))
    kb.adjust(1)
    return kb.as_markup()


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Отправить всем", callback_data=AdminCB(action="bcast_send"), style=ButtonStyle.PRIMARY)
    kb.button(text="❌ Отмена", callback_data=AdminCB(action="menu"), style=ButtonStyle.DANGER)
    kb.adjust(2)
    return kb.as_markup()
