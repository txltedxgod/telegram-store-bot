"""Aggregated statistics for the admin dashboard."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Order, OrderStatus, User


@dataclass
class Stats:
    users: int
    orders: int
    revenue: Decimal
    users_today: int
    orders_today: int


async def collect(session: AsyncSession) -> Stats:
    start_of_day = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    users = await session.scalar(select(func.count(User.id))) or 0
    orders = await session.scalar(select(func.count(Order.id))) or 0
    revenue = await session.scalar(
        select(func.coalesce(func.sum(Order.total_price), 0)).where(
            Order.status != OrderStatus.cancelled
        )
    ) or 0
    users_today = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= start_of_day)
    ) or 0
    orders_today = await session.scalar(
        select(func.count(Order.id)).where(Order.created_at >= start_of_day)
    ) or 0

    return Stats(
        users=int(users),
        orders=int(orders),
        revenue=Decimal(revenue),
        users_today=int(users_today),
        orders_today=int(orders_today),
    )
