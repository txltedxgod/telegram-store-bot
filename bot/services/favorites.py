"""Favorites data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Favorite


async def is_favorite(
    session: AsyncSession, user_id: int, product_id: int
) -> bool:
    result = await session.execute(
        select(Favorite.id).where(
            Favorite.user_id == user_id, Favorite.product_id == product_id
        )
    )
    return result.scalar_one_or_none() is not None


async def toggle(
    session: AsyncSession, user_id: int, product_id: int
) -> bool:
    """Toggle favorite; return True if now favorited, False if removed."""
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id, Favorite.product_id == product_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        await session.delete(existing)
        await session.flush()
        return False
    session.add(Favorite(user_id=user_id, product_id=product_id))
    await session.flush()
    return True


async def list_favorites(session: AsyncSession, user_id: int) -> list[Favorite]:
    result = await session.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
    )
    return list(result.scalars().unique().all())
