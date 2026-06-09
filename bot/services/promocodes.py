"""Promocode data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Promocode


async def get_by_code(session: AsyncSession, code: str) -> Promocode | None:
    result = await session.execute(
        select(Promocode).where(Promocode.code == code.strip().upper())
    )
    return result.scalar_one_or_none()


async def get_active(session: AsyncSession, code: str) -> Promocode | None:
    promo = await get_by_code(session, code)
    if promo and promo.is_available:
        return promo
    return None


async def create(
    session: AsyncSession, *, code: str, discount_percent: int, max_uses: int = 0
) -> Promocode:
    promo = Promocode(
        code=code.strip().upper(),
        discount_percent=discount_percent,
        max_uses=max_uses,
    )
    session.add(promo)
    await session.flush()
    return promo


async def mark_used(session: AsyncSession, promo: Promocode) -> None:
    promo.used_count += 1
    await session.flush()


async def list_all(session: AsyncSession) -> list[Promocode]:
    result = await session.execute(select(Promocode).order_by(Promocode.id.desc()))
    return list(result.scalars().all())
