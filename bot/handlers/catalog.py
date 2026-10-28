"""Catalog: categories, product lists and product cards."""
from __future__ import annotations

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
from bot.services import categories as categories_service
from bot.services import cart as cart_service
from bot.services import favorites as favorites_service
from bot.services import products as products_service
from bot.utils.texts import product_card
from bot.utils.ui import render_menu_step

router = Router(name="catalog")


async def _show_product(query: CallbackQuery, session: AsyncSession, user: User, product_id: int, category_id: int) -> None:
    product = await products_service.get_product(session, product_id)
    if product is None:
        await query.answer("Товар не найден", show_alert=True)
        return
    in_fav = await favorites_service.is_favorite(session, user.id, product.id)
    await query.message.edit_text(
        product_card(product),
        reply_markup=product_card_kb(
            product, in_favorites=in_fav, category_id=category_id or product.category_id
        ),
    )
    await query.answer()


@router.callback_query(MenuCB.filter(F.action == "catalog"))
async def show_catalog(query: CallbackQuery, session: AsyncSession) -> None:
    categories = await categories_service.list_categories(session)
    if not categories:
        await query.answer("Каталог пока пуст", show_alert=True)
        return
    await render_menu_step(
        query,
        "🛒 <b>Каталог товаров SEO Store</b>\n────────────────────────\nВыберите интересующую категорию:",
        reply_markup=categories_kb(categories),
    )
    await query.answer()


@router.callback_query(CategoryCB.filter())
async def show_category(
    query: CallbackQuery, callback_data: CategoryCB, session: AsyncSession
) -> None:
    category = await categories_service.get_category(session, callback_data.category_id)
    if category is None:
        await query.answer("Категория не найдена", show_alert=True)
        return
    products = await products_service.list_by_category(session, category.id)
    if not products:
        await query.answer("В этой категории пока нет товаров", show_alert=True)
        return
    await query.message.edit_text(
        f"{category.title}\n\nВыберите товар:",
        reply_markup=products_kb(products, category.id),
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
    product = await products_service.get_product(session, callback_data.product_id)
    if product is None or not product.in_stock:
        await query.answer("Товар недоступен", show_alert=True)
        return
    await cart_service.add_item(session, user.id, product.id, quantity=1)
    await query.answer(f"«{product.name}» добавлен в корзину 🧺", show_alert=False)
