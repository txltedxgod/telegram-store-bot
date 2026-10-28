"""Product search (FSM) with localization."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.keyboards.callbacks import MenuCB
from bot.keyboards.user import back_home, products_kb
from bot.services import products as products_service
from bot.states import SearchSG
from bot.utils.texts import get_lang
from bot.utils.ui import render_menu_step

router = Router(name="search")


@router.callback_query(MenuCB.filter(F.action == "search"))
async def start_search(query: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = get_lang(user)
    await state.set_state(SearchSG.query)
    if lang == "en":
        text = (
            "🔍 <b>Product Search</b>\n\n"
            "Enter your search query (e.g. <code>Steam</code>, <code>Windows</code>, <code>VPN</code>, <code>AI</code>):"
        )
    else:
        text = (
            "🔍 <b>Пошук товарів SEO Store</b>\n\n"
            "Введіть пошуковий запит (наприклад: <code>Steam</code>, <code>Windows</code>, <code>VPN</code>, <code>AI</code>):"
        )

    await render_menu_step(
        query,
        text,
        reply_markup=back_home(lang),
    )
    await query.answer()


@router.message(SearchSG.query)
async def process_search(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    lang = get_lang(user)
    query_text = (message.text or "").strip()
    if not query_text:
        warning = "Please enter search keywords." if lang == "en" else "Будь ласка, введіть текст для пошуку."
        await message.answer(warning)
        return

    await state.clear()
    results = await products_service.search_products(session, query_text)
    if not results:
        not_found = (
            f"No products found for «<b>{query_text}</b>».\n\n"
            "Try another keyword or browse the catalog:"
            if lang == "en"
            else f"За запитом «<b>{query_text}</b>» нічого не знайдено.\n\n"
            "Спробуйте змінити запит або перегляньте каталог:"
        )
        await message.answer(
            not_found,
            reply_markup=back_home(lang),
            parse_mode="HTML",
        )
        return

    if lang == "en":
        title = (
            f"🔍 <b>Search results for «{query_text}»:</b>\n"
            f"Items found: <b>{len(results)}</b>\n\n"
            "Select an item to view details:"
        )
    else:
        title = (
            f"🔍 <b>Результати пошуку за «{query_text}»:</b>\n"
            f"Знайдено товарів: <b>{len(results)}</b>\n\n"
            "Оберіть товар для перегляду деталей:"
        )

    await message.answer(
        title,
        reply_markup=products_kb(results, category_id=results[0].category_id, lang=lang),
        parse_mode="HTML",
    )
