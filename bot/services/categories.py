"""Category data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Category


async def list_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(select(Category).order_by(Category.id))
    return list(result.scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def get_or_create_category(
    session: AsyncSession, name: str, emoji: str | None = None
) -> Category:
    result = await session.execute(select(Category).where(Category.name == name))
    category = result.scalar_one_or_none()
    if category is None:
        category = Category(name=name, emoji=emoji)
        session.add(category)
        await session.flush()
    return category


# Convenient aliases
get_all = list_categories
create = get_or_create_category
