"""Order creation and management."""
from __future__ import annotations

import csv
import io
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    CartItem,
    Order,
    OrderItem,
    OrderStatus,
    Promocode,
)
from bot.services import cart as cart_service
from bot.services import products as products_service


class CheckoutError(Exception):
    """Raised when an order cannot be created."""


async def create_from_cart(
    session: AsyncSession,
    *,
    user_id: int,
    contact: str | None,
    comment: str | None,
    promocode: Promocode | None = None,
) -> Order:
    items: list[CartItem] = await cart_service.get_items(session, user_id)
    if not items:
        raise CheckoutError("Корзина пуста")

    # Validate stock before committing.
    for item in items:
        if item.quantity > item.product.stock:
            raise CheckoutError(
                f"Недостаточно товара «{item.product.name}» на складе"
            )

    subtotal = cart_service.total(items)
    discount = Decimal("0")
    if promocode is not None and promocode.is_available:
        discount = (subtotal * Decimal(promocode.discount_percent) / Decimal(100)).quantize(
            Decimal("1")
        )
    total_price = max(Decimal("0"), subtotal - discount)

    order = Order(
        user_id=user_id,
        status=OrderStatus.pending,
        total_price=total_price,
        discount=discount,
        contact=contact,
        comment=comment,
        promocode_id=promocode.id if promocode else None,
    )
    session.add(order)
    await session.flush()

    for item in items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=Decimal(item.product.price),
            )
        )
        await products_service.decrement_stock(session, item.product, item.quantity)

    if promocode is not None and discount > 0:
        promocode.used_count += 1

    await cart_service.clear(session, user_id)
    await session.flush()
    await session.refresh(order)
    return order


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    return await session.get(Order, order_id)


async def list_user_orders(
    session: AsyncSession, user_id: int, limit: int = 20
) -> list[Order]:
    result = await session.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_recent(session: AsyncSession, limit: int = 20) -> list[Order]:
    result = await session.execute(
        select(Order).order_by(Order.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def update_status(
    session: AsyncSession, order: Order, status: OrderStatus
) -> None:
    order.status = status
    await session.flush()


async def export_csv(session: AsyncSession) -> bytes:
    """Export every order as CSV bytes (UTF-8 with BOM for Excel)."""
    result = await session.execute(select(Order).order_by(Order.id))
    orders = list(result.scalars().all())

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["order_id", "user_id", "status", "total_price", "discount", "contact", "created_at"]
    )
    for order in orders:
        writer.writerow(
            [
                order.id,
                order.user_id,
                order.status.value,
                order.total_price,
                order.discount,
                order.contact or "",
                order.created_at.isoformat() if order.created_at else "",
            ]
        )
    return buffer.getvalue().encode("utf-8-sig")
