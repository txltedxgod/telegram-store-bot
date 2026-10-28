"""Product data access."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import OrderItem, Product


async def list_by_category(
    session: AsyncSession, category_id: int, *, only_active: bool = True
) -> list[Product]:
    stmt = select(Product).where(Product.category_id == category_id)
    if only_active:
        stmt = stmt.where(Product.is_active.is_(True))
    stmt = stmt.order_by(Product.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


async def get_by_name_and_category(
    session: AsyncSession, name: str, category_id: int
) -> Product | None:
    result = await session.execute(
        select(Product).where(
            Product.name == name, Product.category_id == category_id
        )
    )
    return result.scalar_one_or_none()


async def list_all(session: AsyncSession) -> list[Product]:
    result = await session.execute(select(Product).order_by(Product.id))
    return list(result.scalars().all())


async def search(session: AsyncSession, query: str) -> list[Product]:
    pattern = f"%{query.strip()}%"
    result = await session.execute(
        select(Product)
        .where(Product.is_active.is_(True), Product.name.ilike(pattern))
        .order_by(Product.name)
        .limit(25)
    )
    return list(result.scalars().all())


search_products = search


async def create_product(
    session: AsyncSession,
    *,
    name: str,
    price: Decimal,
    description: str,
    category_id: int,
    stock: int,
) -> Product:
    product = Product(
        name=name,
        price=price,
        description=description,
        category_id=category_id,
        stock=stock,
    )
    session.add(product)
    await session.flush()
    return product


create = create_product


async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.flush()


async def update_field(
    session: AsyncSession, product: Product, field: str, value: object
) -> None:
    setattr(product, field, value)
    await session.flush()


async def decrement_stock(
    session: AsyncSession, product: Product, quantity: int
) -> None:
    product.stock = max(0, product.stock - quantity)
    await session.flush()


async def top_products(
    session: AsyncSession, limit: int = 10
) -> list[tuple[str, int]]:
    """Best sellers by total quantity ordered."""
    result = await session.execute(
        select(
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("sold"),
        )
        .group_by(OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
    )
    return [(row[0], int(row[1])) for row in result.all()]
