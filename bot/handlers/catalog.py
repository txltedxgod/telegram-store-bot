"""Catalog: categories, product lists and product cards with animated GIF banner."""
from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import CategoryCB, MenuCB, ProductCB
from bot.keyboards.user import (
    categories_kb,
    product_card_kb,
    products_kb,
)
from bot.services import cart as cart_service
from bot.services import categories as categories_service
from bot.services import favorites as favorites_service
from bot.services import products as products_service
from bot.utils.emojis import EMOJI_CATALOG, ce
from bot.utils.texts import get_lang, product_card
from bot.utils.ui import render_animation_step, render_menu_step

router = Router(name="catalog")

CATALOG_GIF_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "catalog.gif"


async def _show_product(
    query: CallbackQuery, session: AsyncSession, user: User, product_id: int, category_id: int
) -> None:
    lang = get_lang(user)
    product = await products_service.get_product(session, product_id)
    if product is None:
        not_found = "Product not found" if lang == "en" else "Товар не знайдено"
        await query.answer(not_found, show_alert=True)
        return
    in_fav = await favorites_service.is_favorite(session, user.id, product.id)
    text = product_card(product, user)
    kb = product_card_kb(
        product, in_favorites=in_fav, category_id=category_id or product.category_id, lang=lang
    )
    await render_menu_step(query, text, reply_markup=kb)
    await query.answer()


@router.callback_query(MenuCB.filter(F.action == "catalog"))
async def show_catalog(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = get_lang(user)
    categories = await categories_service.list_categories(session)
    if not categories:
        empty = "Catalog is currently empty" if lang == "en" else "Каталог наразі порожній"
        await query.answer(empty, show_alert=True)
        return

    icon_catalog = ce(EMOJI_CATALOG, "🛍")
    if lang == "en":
        caption = (
            f"{icon_catalog} <b>SEO Store Digital Catalog</b>\n\n"
            f"Select a category below to browse items:"
        )
    else:
        caption = (
            f"{icon_catalog} <b>Каталог товарів SEO Store</b>\n\n"
            f"Оберіть категорію для перегляду товарів:"
        )

    await render_animation_step(
        query,
        CATALOG_GIF_PATH,
        caption,
        reply_markup=categories_kb(categories, lang=lang),
    )
    await query.answer()


@router.callback_query(CategoryCB.filter())
async def show_category(
    query: CallbackQuery, callback_data: CategoryCB, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    category = await categories_service.get_category(session, callback_data.category_id)
    if category is None:
        not_found = "Category not found" if lang == "en" else "Категорію не знайдено"
        await query.answer(not_found, show_alert=True)
        return
    products = await products_service.list_by_category(session, category.id)
    if not products:
        empty = "No items in this category yet" if lang == "en" else "У цій категорії поки немає товарів"
        await query.answer(empty, show_alert=True)
        return

    prompt = "Select an item:" if lang == "en" else "Оберіть товар:"
    text = f"💎 <b>{category.title}</b>\n\n{prompt}"
    await render_menu_step(
        query,
        text,
        reply_markup=products_kb(products, category.id, lang=lang),
    )
    await query.answer()


@router.callback_query(ProductCB.filter(F.action == "view"))
async def view_product(
    query: CallbackQuery, callback_data: ProductCB, session: AsyncSession, user: User
) -> None:
    await _show_product(
        query, session, user, callback_data.product_id, callback_data.category_id
    )


@router.callback_query(ProductCB.filter(F.action == "buy"))
async def buy_product(
    query: CallbackQuery, callback_data: ProductCB, session: AsyncSession, user: User
) -> None:
    lang = get_lang(user)
    product = await products_service.get_product(session, callback_data.product_id)
    if product is None or not product.in_stock:
        unavailable = "Item is unavailable" if lang == "en" else "Товар недоступний"
        await query.answer(unavailable, show_alert=True)
        return
    await cart_service.add_item(session, user.id, product.id, quantity=1)
    added = f"«{product.name}» added to cart 🧺" if lang == "en" else f"«{product.name}» додано до кошика 🧺"
    await query.answer(added, show_alert=False)
