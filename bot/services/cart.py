"""Shopping cart data access."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import CartItem


async def get_items(session: AsyncSession, user_id: int) -> list[CartItem]:
    result = await session.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .order_by(CartItem.id)
    )
    return list(result.scalars().unique().all())


async def get_item(
    session: AsyncSession, user_id: int, product_id: int
) -> CartItem | None:
    result = await session.execute(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )
    return result.scalars().unique().one_or_none()


async def add_item(
    session: AsyncSession, user_id: int, product_id: int, quantity: int = 1
) -> CartItem:
    item = await get_item(session, user_id, product_id)
    if item is None:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(item)
    else:
        item.quantity += quantity
    await session.flush()
    return item


async def change_quantity(
    session: AsyncSession, item: CartItem, delta: int
) -> CartItem | None:
    item.quantity += delta
    if item.quantity <= 0:
        await session.delete(item)
        await session.flush()
        return None
    await session.flush()
    return item


async def remove_item(session: AsyncSession, user_id: int, product_id: int) -> None:
    await session.execute(
        delete(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )
    await session.flush()


async def clear(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await session.flush()


def total(items: list[CartItem]) -> Decimal:
    return sum((Decimal(i.product.price) * i.quantity for i in items), Decimal("0"))
