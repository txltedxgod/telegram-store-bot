"""Inline keyboards for the customer-facing part of the bot with UK/EN localization."""
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
    LanguageCB,
    MenuCB,
    OrderCB,
    ProductCB,
)
from bot.utils.texts import money, status_label


def language_selection_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇦 Українська", callback_data=LanguageCB(code="uk"))
    kb.button(text="🇬🇧 English", callback_data=LanguageCB(code="en"))
    kb.adjust(2)
    return kb.as_markup()


def main_menu(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if lang == "en":
        kb.button(text="🛒 Catalog", callback_data=MenuCB(action="catalog"), style=ButtonStyle.PRIMARY)
        kb.button(text="🧺 Cart", callback_data=MenuCB(action="cart"))
        kb.button(text="📦 My Orders", callback_data=MenuCB(action="orders"))
        kb.button(text="👤 Profile", callback_data=MenuCB(action="profile"))
        kb.button(text="⭐ Favorites", callback_data=MenuCB(action="favorites"))
        kb.button(text="🔍 Search", callback_data=MenuCB(action="search"))
        kb.button(text="🎁 Referrals", callback_data=MenuCB(action="referral"))
        kb.button(text="🌐 Language", callback_data=MenuCB(action="language"))
    else:
        kb.button(text="🛒 Каталог товарів", callback_data=MenuCB(action="catalog"), style=ButtonStyle.PRIMARY)
        kb.button(text="🧺 Кошик", callback_data=MenuCB(action="cart"))
        kb.button(text="📦 Мої замовлення", callback_data=MenuCB(action="orders"))
        kb.button(text="👤 Особистий кабінет", callback_data=MenuCB(action="profile"))
        kb.button(text="⭐ Обране", callback_data=MenuCB(action="favorites"))
        kb.button(text="🔍 Пошук", callback_data=MenuCB(action="search"))
        kb.button(text="🎁 Реферали та Бонуси", callback_data=MenuCB(action="referral"))
        kb.button(text="🌐 Змінити мову", callback_data=MenuCB(action="language"))
    kb.adjust(1, 2, 2, 2, 1)
    return kb.as_markup()


def back_home(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(text=text, callback_data=MenuCB(action="home"))
    return kb.as_markup()


def categories_kb(categories: list[Category], lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(
            text=category.title,
            callback_data=CategoryCB(category_id=category.id),
        )
    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(text=back_text, callback_data=MenuCB(action="home"))
    kb.adjust(1)
    return kb.as_markup()


def products_kb(products: list[Product], category_id: int, lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(
            text=f"{product.name} — {money(product.price)}",
            callback_data=ProductCB(
                action="view", product_id=product.id, category_id=category_id
            ),
        )
    back_text = "« To Categories" if lang == "en" else "« До категорій"
    kb.button(text=back_text, callback_data=MenuCB(action="catalog"))
    kb.adjust(1)
    return kb.as_markup()


def product_card_kb(
    product: Product, *, in_favorites: bool, category_id: int, lang: str = "uk"
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    buy_text = "🛒 Buy Now" if lang == "en" else "🛒 Купити"
    if product.in_stock:
        kb.button(
            text=buy_text,
            callback_data=ProductCB(
                action="buy", product_id=product.id, category_id=category_id
            ),
            style=ButtonStyle.PRIMARY,
        )
    if in_favorites:
        fav_text = "💔 Remove from Favorites" if lang == "en" else "💔 Прибрати з обраного"
    else:
        fav_text = "⭐ Add to Favorites" if lang == "en" else "⭐ В обране"

    kb.button(
        text=fav_text,
        callback_data=FavoriteCB(
            action="remove" if in_favorites else "add", product_id=product.id
        ),
        style=ButtonStyle.DANGER if in_favorites else None,
    )
    back_text = "« Back" if lang == "en" else "« Назад"
    kb.button(
        text=back_text,
        callback_data=CategoryCB(category_id=category_id),
    )
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items: list[CartItem], lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        unit = "pcs" if lang == "en" else "шт."
        kb.button(text=f"➖ {item.product.name}", callback_data=CartCB(action="dec", product_id=item.product_id))
        kb.button(text=f"{item.quantity} {unit}", callback_data=CartCB(action="noop", product_id=item.product_id))
        kb.button(text="➕", callback_data=CartCB(action="inc", product_id=item.product_id))
        kb.button(text="🗑", callback_data=CartCB(action="remove", product_id=item.product_id), style=ButtonStyle.DANGER)
    if items:
        checkout_text = "✅ Checkout Order" if lang == "en" else "✅ Оформити замовлення"
        clear_text = "🧹 Clear Cart" if lang == "en" else "🧹 Очистити"
        kb.button(text=checkout_text, callback_data=CartCB(action="checkout"), style=ButtonStyle.SUCCESS)
        kb.button(text=clear_text, callback_data=CartCB(action="clear"), style=ButtonStyle.DANGER)

    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(text=back_text, callback_data=MenuCB(action="home"))
    
    rows = [4] * len(items)
    if items:
        rows += [1, 1]
    rows += [1]
    kb.adjust(*rows)
    return kb.as_markup()


def payment_methods_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if lang == "en":
        kb.button(text="💳 Card (UAH / Monobank / PrivatBank)", callback_data=CheckoutCB(action="pay_method", method="card_uah"))
        kb.button(text="⚡️ Crypto (USDT TRC20 / TON / BTC)", callback_data=CheckoutCB(action="pay_method", method="crypto"))
        kb.button(text="❌ Cancel", callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    else:
        kb.button(text="💳 Гривня (Картка Monobank / ПриватБанк)", callback_data=CheckoutCB(action="pay_method", method="card_uah"))
        kb.button(text="⚡️ Криптовалюта (USDT TRC-20 / TON / BTC)", callback_data=CheckoutCB(action="pay_method", method="crypto"))
        kb.button(text="❌ Скасувати", callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    kb.adjust(1)
    return kb.as_markup()


def orders_kb(orders: list[Order], lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for order in orders:
        kb.button(
            text=f"#{order.id} — {status_label(order.status, lang)}",
            callback_data=OrderCB(order_id=order.id),
        )
    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(text=back_text, callback_data=MenuCB(action="home"))
    kb.adjust(1)
    return kb.as_markup()


def order_detail_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    back_text = "« Back to Orders" if lang == "en" else "« До замовлень"
    kb.button(text=back_text, callback_data=MenuCB(action="orders"))
    return kb.as_markup()


def checkout_comment_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    skip_text = "⏭ Skip" if lang == "en" else "⏭ Пропустити"
    cancel_text = "❌ Cancel" if lang == "en" else "❌ Скасувати"
    kb.button(text=skip_text, callback_data=CheckoutCB(action="skip"))
    kb.button(text=cancel_text, callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    kb.adjust(2)
    return kb.as_markup()


def checkout_cancel_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    cancel_text = "❌ Cancel" if lang == "en" else "❌ Скасувати"
    kb.button(text=cancel_text, callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    return kb.as_markup()


def favorites_kb(favorites: list[Favorite], lang: str = "uk") -> InlineKeyboardMarkup:
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
    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(text=back_text, callback_data=MenuCB(action="home"))
    kb.adjust(1)
    return kb.as_markup()
