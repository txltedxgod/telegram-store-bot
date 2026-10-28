"""Inline keyboards for the customer-facing part of the bot with UK/EN localization
and native Telegram custom premium emojis on buttons (icon_custom_emoji_id).
"""
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
from bot.utils.emojis import (
    EMOJI_CARD,
    EMOJI_CART,
    EMOJI_CHECK,
    EMOJI_GAME,
    EMOJI_GIFT,
    EMOJI_KEY,
    EMOJI_LANGUAGE,
    EMOJI_LIGHTNING,
    EMOJI_ORDERS,
    EMOJI_PROFILE,
    EMOJI_ROBOT,
    EMOJI_SEARCH,
    EMOJI_SHIELD,
    EMOJI_STAR,
    EMOJI_STORE,
)
from bot.utils.texts import money, status_label


def get_category_custom_emoji(name: str) -> str:
    lower = name.lower()
    if "підписк" in lower or "premium" in lower:
        return EMOJI_STAR
    if "ai" in lower or "нейро" in lower:
        return EMOJI_ROBOT
    if "софт" in lower or "ліценз" in lower:
        return EMOJI_KEY
    if "безпек" in lower or "vpn" in lower:
        return EMOJI_SHIELD
    if "ігр" in lower or "steam" in lower or "game" in lower:
        return EMOJI_GAME
    return EMOJI_STORE


def language_selection_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇦 Українська", callback_data=LanguageCB(code="uk"))
    kb.button(text="🇬🇧 English", callback_data=LanguageCB(code="en"))
    kb.adjust(2)
    return kb.as_markup()


def main_menu(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if lang == "en":
        kb.button(
            text="Catalog",
            callback_data=MenuCB(action="catalog"),
            icon_custom_emoji_id=EMOJI_STORE,
            style=ButtonStyle.PRIMARY,
        )
        kb.button(
            text="Cart",
            callback_data=MenuCB(action="cart"),
            icon_custom_emoji_id=EMOJI_CART,
        )
        kb.button(
            text="My Orders",
            callback_data=MenuCB(action="orders"),
            icon_custom_emoji_id=EMOJI_ORDERS,
        )
        kb.button(
            text="Profile",
            callback_data=MenuCB(action="profile"),
            icon_custom_emoji_id=EMOJI_PROFILE,
        )
        kb.button(
            text="Favorites",
            callback_data=MenuCB(action="favorites"),
            icon_custom_emoji_id=EMOJI_STAR,
        )
        kb.button(
            text="Search",
            callback_data=MenuCB(action="search"),
            icon_custom_emoji_id=EMOJI_SEARCH,
        )
        kb.button(
            text="Referrals",
            callback_data=MenuCB(action="referral"),
            icon_custom_emoji_id=EMOJI_GIFT,
        )
        kb.button(
            text="Language",
            callback_data=MenuCB(action="language"),
            icon_custom_emoji_id=EMOJI_LANGUAGE,
        )
    else:
        kb.button(
            text="Каталог товарів",
            callback_data=MenuCB(action="catalog"),
            icon_custom_emoji_id=EMOJI_STORE,
            style=ButtonStyle.PRIMARY,
        )
        kb.button(
            text="Кошик",
            callback_data=MenuCB(action="cart"),
            icon_custom_emoji_id=EMOJI_CART,
        )
        kb.button(
            text="Мої замовлення",
            callback_data=MenuCB(action="orders"),
            icon_custom_emoji_id=EMOJI_ORDERS,
        )
        kb.button(
            text="Особистий кабінет",
            callback_data=MenuCB(action="profile"),
            icon_custom_emoji_id=EMOJI_PROFILE,
        )
        kb.button(
            text="Обране",
            callback_data=MenuCB(action="favorites"),
            icon_custom_emoji_id=EMOJI_STAR,
        )
        kb.button(
            text="Пошук",
            callback_data=MenuCB(action="search"),
            icon_custom_emoji_id=EMOJI_SEARCH,
        )
        kb.button(
            text="Реферали та Бонуси",
            callback_data=MenuCB(action="referral"),
            icon_custom_emoji_id=EMOJI_GIFT,
        )
        kb.button(
            text="Змінити мову",
            callback_data=MenuCB(action="language"),
            icon_custom_emoji_id=EMOJI_LANGUAGE,
        )
    kb.adjust(1, 2, 2, 2, 1)
    return kb.as_markup()


def back_home(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(
        text=text,
        callback_data=MenuCB(action="home"),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    return kb.as_markup()


def categories_kb(categories: list[Category], lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        emoji_id = get_category_custom_emoji(category.name)
        # Strip duplicate emojis from beginning of name if present
        clean_name = category.name.lstrip("⚡️💎🧠🤖🔑💻🌐🛡🎮🕹 ").strip()
        kb.button(
            text=clean_name,
            callback_data=CategoryCB(category_id=category.id),
            icon_custom_emoji_id=emoji_id,
        )
    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(
        text=back_text,
        callback_data=MenuCB(action="home"),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    kb.adjust(1)
    return kb.as_markup()


def products_kb(products: list[Product], category_id: int, lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for product in products:
        clean_name = product.name.lstrip("⭐️🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
        kb.button(
            text=f"{clean_name} • {money(product.price)}",
            callback_data=ProductCB(
                action="view", product_id=product.id, category_id=category_id
            ),
            icon_custom_emoji_id=EMOJI_STAR,
        )
    back_text = "« To Categories" if lang == "en" else "« До категорій"
    kb.button(
        text=back_text,
        callback_data=MenuCB(action="catalog"),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    kb.adjust(1)
    return kb.as_markup()


def product_card_kb(
    product: Product, *, in_favorites: bool, category_id: int, lang: str = "uk"
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    buy_text = "Купити" if lang == "uk" else "Buy Now"
    if product.in_stock:
        kb.button(
            text=buy_text,
            callback_data=ProductCB(
                action="buy", product_id=product.id, category_id=category_id
            ),
            icon_custom_emoji_id=EMOJI_CART,
            style=ButtonStyle.PRIMARY,
        )
    if in_favorites:
        fav_text = "Прибрати з обраного" if lang == "uk" else "Remove from Favorites"
    else:
        fav_text = "В обране" if lang == "uk" else "Add to Favorites"

    kb.button(
        text=fav_text,
        callback_data=FavoriteCB(
            action="remove" if in_favorites else "add", product_id=product.id
        ),
        icon_custom_emoji_id=EMOJI_STAR,
        style=ButtonStyle.DANGER if in_favorites else None,
    )
    back_text = "« Назад" if lang == "uk" else "« Back"
    kb.button(
        text=back_text,
        callback_data=CategoryCB(category_id=category_id),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items: list[CartItem], lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        unit = "pcs" if lang == "en" else "шт."
        clean_name = item.product.name.lstrip("⭐️🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
        kb.button(text=f"➖ {clean_name}", callback_data=CartCB(action="dec", product_id=item.product_id))
        kb.button(text=f"{item.quantity} {unit}", callback_data=CartCB(action="noop", product_id=item.product_id))
        kb.button(text="➕", callback_data=CartCB(action="inc", product_id=item.product_id))
        kb.button(text="🗑", callback_data=CartCB(action="remove", product_id=item.product_id), style=ButtonStyle.DANGER)
    if items:
        checkout_text = "Оформити замовлення" if lang == "uk" else "Checkout Order"
        clear_text = "Очистити" if lang == "uk" else "Clear Cart"
        kb.button(
            text=checkout_text,
            callback_data=CartCB(action="checkout"),
            icon_custom_emoji_id=EMOJI_CHECK,
            style=ButtonStyle.SUCCESS,
        )
        kb.button(
            text=clear_text,
            callback_data=CartCB(action="clear"),
            style=ButtonStyle.DANGER,
        )

    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(
        text=back_text,
        callback_data=MenuCB(action="home"),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    
    rows = [4] * len(items)
    if items:
        rows += [1, 1]
    rows += [1]
    kb.adjust(*rows)
    return kb.as_markup()


def payment_methods_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if lang == "en":
        kb.button(
            text="Card (UAH Monobank / PrivatBank)",
            callback_data=CheckoutCB(action="pay_method", method="card_uah"),
            icon_custom_emoji_id=EMOJI_CARD,
        )
        kb.button(
            text="Crypto (USDT TRC20 / TON / BTC)",
            callback_data=CheckoutCB(action="pay_method", method="crypto"),
            icon_custom_emoji_id=EMOJI_LIGHTNING,
        )
        kb.button(text="Cancel", callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    else:
        kb.button(
            text="Гривня (Картка Monobank / ПриватБанк)",
            callback_data=CheckoutCB(action="pay_method", method="card_uah"),
            icon_custom_emoji_id=EMOJI_CARD,
        )
        kb.button(
            text="Криптовалюта (USDT TRC-20 / TON / BTC)",
            callback_data=CheckoutCB(action="pay_method", method="crypto"),
            icon_custom_emoji_id=EMOJI_LIGHTNING,
        )
        kb.button(text="Скасувати", callback_data=CheckoutCB(action="cancel"), style=ButtonStyle.DANGER)
    kb.adjust(1)
    return kb.as_markup()


def orders_kb(orders: list[Order], lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for order in orders:
        label = status_label(order.status, lang).lstrip("⏳💳✅❌ ")
        kb.button(
            text=f"#{order.id} • {label}",
            callback_data=OrderCB(order_id=order.id),
            icon_custom_emoji_id=EMOJI_ORDERS,
        )
    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(
        text=back_text,
        callback_data=MenuCB(action="home"),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    kb.adjust(1)
    return kb.as_markup()


def order_detail_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    back_text = "« Back to Orders" if lang == "en" else "« До замовлень"
    kb.button(
        text=back_text,
        callback_data=MenuCB(action="orders"),
        icon_custom_emoji_id=EMOJI_ORDERS,
    )
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
        clean_name = fav.product.name.lstrip("⭐️🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").strip()
        kb.button(
            text=f"{clean_name} • {money(fav.product.price)}",
            callback_data=ProductCB(
                action="view",
                product_id=fav.product_id,
                category_id=fav.product.category_id,
            ),
            icon_custom_emoji_id=EMOJI_STAR,
        )
    back_text = "« Main Menu" if lang == "en" else "« В меню"
    kb.button(
        text=back_text,
        callback_data=MenuCB(action="home"),
        icon_custom_emoji_id=EMOJI_STORE,
    )
    kb.adjust(1)
    return kb.as_markup()
