"""Product search (FSM)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.callbacks import MenuCB
from bot.keyboards.user import back_home, products_kb
from bot.services import products as products_service
from bot.states import SearchSG
from bot.utils.ui import render_menu_step

router = Router(name="search")


@router.callback_query(MenuCB.filter(F.action == "search"))
async def start_search(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchSG.query)
    await render_menu_step(
        query,
        "🔍 <b>Поиск товаров SEO Store</b>\n"
        "────────────────────────\n"
        "Введите поисковый запрос (например: <code>Steam</code>, <code>Windows</code>, <code>VPN</code>, <code>AI</code>):",
        reply_markup=back_home(),
    )
    await query.answer()


@router.message(SearchSG.query)
async def process_search(message: Message, state: FSMContext, session: AsyncSession) -> None:
    query_text = (message.text or "").strip()
    if not query_text:
        await message.answer("Пожалуйста, введите текст для поиска.")
        return

    await state.clear()
    results = await products_service.search_products(session, query_text)
    if not results:
        await message.answer(
            f"По запросу «<b>{query_text}</b>» ничего не найдено.\n\n"
            "Попробуйте изменить запрос или откройте каталог:",
            reply_markup=back_home(),
        )
        return

    await message.answer(
        f"🔍 <b>Результаты поиска по «{query_text}»:</b>\n"
        f"Найдено товаров: <b>{len(results)}</b>\n\n"
        "Выберите товар для просмотра деталей:",
        reply_markup=products_kb(results, category_id=results[0].category_id),
    )
