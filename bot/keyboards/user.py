"""Inline keyboards for the customer-facing part of the bot."""
from __future__ import annotations

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import CartItem, Category, Favorite, Order, Product
from bot.keyboards.callbacks import (
    CartCB,
    CategoryCB,
    CheckoutCB,
    FavoriteCB,
    MenuCB,
    OrderCB,
    ProductCB,
)
from bot.utils.texts import money, status_label


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Каталог", callback_data=MenuCB(action="catalog"), style=ButtonStyle.PRIMARY)
    kb.button(text="🧺 Корзина", callback_data=MenuCB(action="cart"))
    kb.button(text="📦 Мои заказы", callback_data=MenuCB(action="orders"))
    kb.button(text="👤 Профиль", callback_data=MenuCB(action="profile"))
    kb.button(text="⭐ Избранное", callback_data=MenuCB(action="favorites"))
    kb.button(text="🔍 Поиск", callback_data=MenuCB(action="search"))
    kb.adjust(2, 2, 2)
    return kb.as_markup()


def back_home() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="« В меню", callback_data=MenuCB(action="home"))
    return kb.as_markup()


def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(
            text=category.title,
            callback_data=CategoryCB(category_id=category.id),
        )
    kb.button(text="« В меню", callback_data=MenuCB(action="home"))
    kb.adjust(1)
    return kb.as_markup()


def products_kb(products: list[Product], category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(
            text=f"{product.name} — {money(product.price)}",
            callback_data=ProductCB(
                action="view", product_id=product.id, category_id=category_id
            ),
        )
    kb.button(text="« К категориям", callback_data=MenuCB(action="catalog"))
    kb.adjust(1)
    return kb.as_markup()


def product_card_kb(
    product: Product, *, in_favorites: bool, category_id: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if product.in_stock:
        kb.button(
            text="🛒 Купить",
            callback_data=ProductCB(
                action="buy", product_id=product.id, category_id=category_id
            ),
            style=ButtonStyle.PRIMARY,
        )
    fav_text = "💔 Убрать из избранного" if in_favorites else "⭐ В избранное"
    kb.button(
        text=fav_text,
        callback_data=FavoriteCB(
            action="remove" if in_favorites else "add", product_id=product.id
        ),
        style=ButtonStyle.DANGER if in_favorites else None,
    )
    kb.button(
        text="« Назад",
        callback_data=CategoryCB(category_id=category_id),
    )
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items: list[CartItem]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=f"➖ {item.product.name}", callback_data=CartCB(action="dec", product_id=item.product_id))
        kb.button(text=f"{item.quantity} шт.", callback_data=CartCB(action="noop", product_id=item.product_id))
        kb.button(text="➕", callback_data=CartCB(action="inc", product_id=item.product_id))
        kb.button(text="🗑", callback_data=CartCB(action="remove", product_id=item.product_id), style=ButtonStyle.DANGER)
    if items:
        kb.button(text="✅ Оформить заказ", callback_data=CartCB(action="checkout"), style=ButtonStyle.SUCCESS)
        kb.button(text="🧹 Очистить", callback_data=CartCB(action="clear"), style=ButtonStyle.DANGER)
    kb.button(text="« В меню", callback_data=MenuCB(action="home"))
    # 4 controls per cart row, then action buttons one per row
    rows = [4] * len(items)
    if items:
        rows += [1, 1]
    rows += [1]
    kb.adjust(*rows)
    return kb.as_markup()


def orders_kb(orders: list[Order]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for order in orders:
        kb.button(
            text=f"#{order.id} — {status_label(order.status)}",
            callback_data=OrderCB(order_id=order.id),
        )
    kb.button(text="« В меню", callback_data=MenuCB(action="home"))
    kb.adjust(1)
    return kb.as_markup()


def order_detail_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="« К заказам", callback_data=MenuCB(action="orders"))
    return kb.as_markup()


def checkout_comment_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⏭ Пропустить", callback_data=CheckoutCB(action="skip"))
    kb.button(text="❌ Отмена", callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    kb.adjust(2)
    return kb.as_markup()


def checkout_cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    return kb.as_markup()


def favorites_kb(favorites: list[Favorite]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for fav in favorites:
        kb.button(
            text=f"{fav.product.name} — {money(fav.product.price)}",
            callback_data=ProductCB(
                action="view",
                product_id=fav.product_id,
                category_id=fav.product.category_id,
            ),
        )
    kb.button(text="« В меню", callback_data=MenuCB(action="home"))
    kb.adjust(1)
    return kb.as_markup()
