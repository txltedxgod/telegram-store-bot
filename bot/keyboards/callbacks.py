"""Typed callback-data factories (aiogram 3)."""
from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    # catalog | cart | orders | profile | favorites | search | home | language
    action: str


class LanguageCB(CallbackData, prefix="lang"):
    code: str  # "uk" | "en"


class CategoryCB(CallbackData, prefix="cat"):
    category_id: int


class ProductCB(CallbackData, prefix="prod"):
    action: str  # view | buy | fav
    product_id: int
    category_id: int = 0


class CartCB(CallbackData, prefix="cart"):
    action: str  # inc | dec | remove | clear | checkout
    product_id: int = 0


class OrderCB(CallbackData, prefix="order"):
    order_id: int


class CheckoutCB(CallbackData, prefix="checkout"):
    action: str  # confirm | cancel | skip | pay_method
    method: str = ""


class FavoriteCB(CallbackData, prefix="fav"):
    action: str  # add | remove
    product_id: int


class AdminCB(CallbackData, prefix="adm"):
    # menu | add | delete | edit | orders | stats | broadcast | promo | export | top
    action: str
    item_id: int = 0
    value: str = ""
