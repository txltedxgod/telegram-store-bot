"""Admin panel: products, orders, stats, broadcast, promocodes, export."""
from __future__ import annotations

import asyncio
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import OrderStatus, User
from bot.filters import IsAdmin
from bot.keyboards.admin import (
    admin_menu,
    admin_order_kb,
    admin_orders_kb,
    back_admin,
    broadcast_confirm_kb,
    categories_pick_kb,
    edit_field_kb,
    products_pick_kb,
)
from bot.keyboards.callbacks import AdminCB
from bot.services import categories as categories_service
from bot.services import orders as orders_service
from bot.services import products as products_service
from bot.services import promocodes as promocodes_service
from bot.services import stats as stats_service
from bot.services import users as users_service
from bot.states import AddProductSG, BroadcastSG, EditProductSG, PromocodeSG
from bot.utils.logger import get_logger
from bot.utils.texts import money, order_card

logger = get_logger("bot.admin")
router = Router(name="admin")
# Every handler in this router requires admin rights.
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

FIELD_LABELS = {
    "name": "название",
    "price": "цену",
    "description": "описание",
    "stock": "остаток",
}


async def _open_menu(message: Message) -> None:
    await message.answer(
        "🛠 <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=admin_menu(),
    )


@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _open_menu(message)


@router.callback_query(AdminCB.filter(F.action == "menu"))
async def admin_menu_cb(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.edit_text(
        "🛠 <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=admin_menu(),
    )
    await query.answer()


# ---------------------------------------------------------------- statistics
@router.callback_query(AdminCB.filter(F.action == "stats"))
async def show_stats(query: CallbackQuery, session: AsyncSession) -> None:
    s = await stats_service.collect(session)
    await query.message.edit_text(
        "📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: <b>{s.users}</b>\n"
        f"📦 Заказов: <b>{s.orders}</b>\n"
        f"💰 Оборот: <b>{money(s.revenue)}</b>\n\n"
        "<b>За сегодня:</b>\n"
        f"+{s.users_today} пользователей\n"
        f"+{s.orders_today} заказов",
        reply_markup=back_admin(),
    )
    await query.answer()


@router.callback_query(AdminCB.filter(F.action == "top"))
async def show_top(query: CallbackQuery, session: AsyncSession) -> None:
    top = await products_service.top_products(session, limit=10)
    if not top:
        await query.answer("Продаж пока нет", show_alert=True)
        return
    lines = ["🏆 <b>Топ популярных товаров</b>\n"]
    for i, (name, sold) in enumerate(top, start=1):
        lines.append(f"{i}. {name} — {sold} шт.")
    await query.message.edit_text("\n".join(lines), reply_markup=back_admin())
    await query.answer()


# ---------------------------------------------------------------- CSV export
@router.callback_query(AdminCB.filter(F.action == "export"))
async def export_orders(query: CallbackQuery, session: AsyncSession) -> None:
    data = await orders_service.export_csv(session)
    await query.message.answer_document(
        BufferedInputFile(data, filename="orders.csv"),
        caption="📄 Экспорт заказов",
    )
    await query.answer("Готово")


# ---------------------------------------------------------------- orders
@router.callback_query(AdminCB.filter(F.action == "orders"))
async def list_orders(query: CallbackQuery, session: AsyncSession) -> None:
    orders = await orders_service.list_recent(session, limit=20)
    if not orders:
        await query.answer("Заказов пока нет", show_alert=True)
        return
    await query.message.edit_text(
        "📦 <b>Последние заказы</b>", reply_markup=admin_orders_kb(orders)
    )
    await query.answer()


@router.callback_query(AdminCB.filter(F.action == "order"))
async def show_order(
    query: CallbackQuery, callback_data: AdminCB, session: AsyncSession
) -> None:
    order = await orders_service.get_order(session, callback_data.item_id)
    if order is None:
        await query.answer("Заказ не найден", show_alert=True)
        return
    await query.message.edit_text(order_card(order), reply_markup=admin_order_kb(order))
    await query.answer()


@router.callback_query(AdminCB.filter(F.action == "setstatus"))
async def set_status(
    query: CallbackQuery, callback_data: AdminCB, session: AsyncSession
) -> None:
    order = await orders_service.get_order(session, callback_data.item_id)
    if order is None:
        await query.answer("Заказ не найден", show_alert=True)
        return
    try:
        new_status = OrderStatus(callback_data.value)
    except ValueError:
        await query.answer("Неверный статус", show_alert=True)
        return
    await orders_service.update_status(session, order, new_status)
    logger.info("Admin %s set order #%s -> %s", query.from_user.id, order.id, new_status.value)
    # Notify the customer about the status change.
    customer = await users_service.get_by_id(session, order.user_id)
    if customer:
        try:
            await query.bot.send_message(
                customer.telegram_id,
                f"ℹ Статус вашего заказа #{order.id} обновлён.",
            )
        except Exception:  # noqa: BLE001
            pass
    await query.message.edit_text(order_card(order), reply_markup=admin_order_kb(order))
    await query.answer("Статус обновлён")


# ---------------------------------------------------------------- delete product
@router.callback_query(AdminCB.filter(F.action == "delete"))
async def delete_pick(query: CallbackQuery, session: AsyncSession) -> None:
    products = await products_service.list_all(session)
    if not products:
        await query.answer("Товаров нет", show_alert=True)
        return
    await query.message.edit_text(
        "❌ Выберите товар для удаления:",
        reply_markup=products_pick_kb(products, action="del"),
    )
    await query.answer()


@router.callback_query(AdminCB.filter(F.action == "del"))
async def delete_product(
    query: CallbackQuery, callback_data: AdminCB, session: AsyncSession
) -> None:
    product = await products_service.get_product(session, callback_data.item_id)
    if product is None:
        await query.answer("Товар не найден", show_alert=True)
        return
    name = product.name
    await products_service.delete_product(session, product)
    logger.info("Admin %s deleted product %s", query.from_user.id, name)
    products = await products_service.list_all(session)
    await query.message.edit_text(
        f"Товар «{name}» удалён.",
        reply_markup=products_pick_kb(products, action="del") if products else back_admin(),
    )
    await query.answer("Удалено")


# ---------------------------------------------------------------- add product (FSM)
@router.callback_query(AdminCB.filter(F.action == "add"))
async def add_start(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddProductSG.name)
    await query.message.edit_text(
        "➕ <b>Добавление товара</b>\n\nВведите название товара:",
        reply_markup=back_admin(),
    )
    await query.answer()


@router.message(AddProductSG.name, F.text)
async def add_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddProductSG.price)
    await message.answer("Введите цену (число):")


@router.message(AddProductSG.price, F.text)
async def add_price(message: Message, state: FSMContext) -> None:
    try:
        price = Decimal(message.text.strip().replace(",", "."))
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        await message.answer("⚠ Введите корректное число, например 100")
        return
    await state.update_data(price=str(price))
    await state.set_state(AddProductSG.description)
    await message.answer("Введите описание товара:")


@router.message(AddProductSG.description, F.text)
async def add_description(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(description=message.text.strip())
    categories = await categories_service.list_categories(session)
    if not categories:
        await state.clear()
        await message.answer("⚠ Сначала создайте категории.", reply_markup=back_admin())
        return
    await state.set_state(AddProductSG.category)
    await message.answer("Выберите категорию:", reply_markup=categories_pick_kb(categories))


@router.callback_query(AddProductSG.category, AdminCB.filter(F.action == "pickcat"))
async def add_category(
    query: CallbackQuery, callback_data: AdminCB, state: FSMContext
) -> None:
    await state.update_data(category_id=callback_data.item_id)
    await state.set_state(AddProductSG.stock)
    await query.message.edit_text("Введите количество (шт.):")
    await query.answer()


@router.message(AddProductSG.stock, F.text)
async def add_stock(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text.strip().isdigit():
        await message.answer("⚠ Введите целое число")
        return
    data = await state.get_data()
    await state.clear()
    product = await products_service.create_product(
        session,
        name=data["name"],
        price=Decimal(data["price"]),
        description=data["description"],
        category_id=data["category_id"],
        stock=int(message.text.strip()),
    )
    logger.info("Admin %s added product %s", message.from_user.id, product.name)
    await message.answer(
        f"✅ Товар «{product.name}» успешно добавлен.",
        reply_markup=back_admin(),
    )


# ---------------------------------------------------------------- edit product (FSM)
@router.callback_query(AdminCB.filter(F.action == "edit"))
async def edit_pick(query: CallbackQuery, session: AsyncSession) -> None:
    products = await products_service.list_all(session)
    if not products:
        await query.answer("Товаров нет", show_alert=True)
        return
    await query.message.edit_text(
        "✏️ Выберите товар для изменения:",
        reply_markup=products_pick_kb(products, action="editpick"),
    )
    await query.answer()


@router.callback_query(AdminCB.filter(F.action == "editpick"))
async def edit_choose_field(
    query: CallbackQuery, callback_data: AdminCB, session: AsyncSession
) -> None:
    product = await products_service.get_product(session, callback_data.item_id)
    if product is None:
        await query.answer("Товар не найден", show_alert=True)
        return
    await query.message.edit_text(
        f"✏️ Товар: <b>{product.name}</b>\nЧто изменить?",
        reply_markup=edit_field_kb(product.id),
    )
    await query.answer()


@router.callback_query(AdminCB.filter(F.action == "editfield"))
async def edit_ask_value(
    query: CallbackQuery, callback_data: AdminCB, state: FSMContext
) -> None:
    await state.set_state(EditProductSG.value)
    await state.update_data(product_id=callback_data.item_id, field=callback_data.value)
    await query.message.edit_text(
        f"Введите новое значение для поля «{FIELD_LABELS.get(callback_data.value, callback_data.value)}»:",
        reply_markup=back_admin(),
    )
    await query.answer()


@router.message(EditProductSG.value, F.text)
async def edit_apply(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    field = data["field"]
    raw = message.text.strip()
    value: object = raw
    if field == "price":
        try:
            value = Decimal(raw.replace(",", "."))
        except InvalidOperation:
            await message.answer("⚠ Введите корректное число")
            return
    elif field == "stock":
        if not raw.isdigit():
            await message.answer("⚠ Введите целое число")
            return
        value = int(raw)
    product = await products_service.get_product(session, data["product_id"])
    if product is None:
        await state.clear()
        await message.answer("Товар не найден.", reply_markup=back_admin())
        return
    await products_service.update_field(session, product, field, value)
    await state.clear()
    logger.info("Admin %s edited product %s field %s", message.from_user.id, product.name, field)
    await message.answer("✅ Товар обновлён.", reply_markup=back_admin())


# ---------------------------------------------------------------- broadcast (FSM)
@router.callback_query(AdminCB.filter(F.action == "broadcast"))
async def broadcast_start(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BroadcastSG.message)
    await query.message.edit_text(
        "📢 Введите текст рассылки:", reply_markup=back_admin()
    )
    await query.answer()


@router.message(BroadcastSG.message, F.text)
async def broadcast_preview(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.html_text)
    await state.set_state(BroadcastSG.confirm)
    await message.answer(
        f"📢 <b>Предпросмотр:</b>\n\n{message.html_text}\n\nОтправить всем пользователям?",
        reply_markup=broadcast_confirm_kb(),
    )


@router.callback_query(BroadcastSG.confirm, AdminCB.filter(F.action == "bcast_send"))
async def broadcast_send(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    await state.clear()
    text = data.get("text", "")
    user_ids = await users_service.all_user_ids(session)
    await query.message.edit_text("📤 Рассылка запущена…")
    await query.answer()

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await query.bot.send_message(uid, text)
            sent += 1
        except Exception:  # noqa: BLE001 - blocked / deleted accounts
            failed += 1
        await asyncio.sleep(0.05)  # ~20 msg/s, stay within Telegram limits

    logger.info("Broadcast finished: success=%s errors=%s", sent, failed)
    await query.message.answer(
        f"✅ Рассылка завершена\n\nУспешно: <b>{sent}</b>\nОшибок: <b>{failed}</b>",
        reply_markup=back_admin(),
    )


# ---------------------------------------------------------------- promocodes (FSM)
@router.callback_query(AdminCB.filter(F.action == "promo"))
async def promo_start(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    promos = await promocodes_service.list_all(session)
    existing = "\n".join(
        f"• <code>{p.code}</code> — {p.discount_percent}% "
        f"({p.used_count}/{p.max_uses or '∞'})"
        for p in promos[:10]
    ) or "пока нет"
    await state.set_state(PromocodeSG.code)
    await query.message.edit_text(
        f"🏷 <b>Промокоды</b>\n\nСуществующие:\n{existing}\n\nВведите код нового промокода:",
        reply_markup=back_admin(),
    )
    await query.answer()


@router.message(PromocodeSG.code, F.text)
async def promo_code(message: Message, state: FSMContext) -> None:
    await state.update_data(code=message.text.strip())
    await state.set_state(PromocodeSG.discount)
    await message.answer("Введите размер скидки в % (1–100):")


@router.message(PromocodeSG.discount, F.text)
async def promo_discount(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit() or not (1 <= int(text) <= 100):
        await message.answer("⚠ Введите число от 1 до 100")
        return
    await state.update_data(discount=int(text))
    await state.set_state(PromocodeSG.max_uses)
    await message.answer("Макс. число использований (0 = без лимита):")


@router.message(PromocodeSG.max_uses, F.text)
async def promo_finish(message: Message, state: FSMContext, session: AsyncSession) -> None:
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠ Введите целое число")
        return
    data = await state.get_data()
    await state.clear()
    promo = await promocodes_service.create(
        session,
        code=data["code"],
        discount_percent=data["discount"],
        max_uses=int(text),
    )
    logger.info("Admin %s created promocode %s", message.from_user.id, promo.code)
    await message.answer(
        f"✅ Промокод <code>{promo.code}</code> на {promo.discount_percent}% создан.",
        reply_markup=back_admin(),
    )
