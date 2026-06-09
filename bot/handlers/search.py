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

router = Router(name="search")


@router.callback_query(MenuCB.filter(F.action == "search"))
async def start_search(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchSG.query)
    await query.message.edit_text(
        "🔍 <b>Поиск товаров</b>\n\nВведите название товара:",
        reply_markup=back_home(),
    )
    await query.answer()


@router.message(SearchSG.query, F.text)
async def run_search(message: Message, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    results = await products_service.search(session, message.text)
    if not results:
        await message.answer(
            "Ничего не найдено 😕", reply_markup=back_home()
        )
        return
    # Reuse the products keyboard; category_id=0 routes \"back\" to the catalog.
    await message.answer(
        f"🔍 Найдено товаров: <b>{len(results)}</b>",
        reply_markup=products_kb(results, category_id=0),
    )
