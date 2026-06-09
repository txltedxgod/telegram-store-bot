"""User-related data access."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Order, OrderStatus, User


async def get_or_create_user(
    session: AsyncSession,
    *,
    telegram_id: int,
    username: str | None = None,
    full_name: str | None = None,
    is_admin: bool = False,
) -> tuple[User, bool]:
    """Return (user, created). Updates username/full_name on every call."""
    user = await get_by_telegram_id(session, telegram_id)
    if user is not None:
        changed = False
        if username != user.username:
            user.username = username
            changed = True
        if full_name != user.full_name:
            user.full_name = full_name
            changed = True
        if is_admin and not user.is_admin:
            user.is_admin = True
            changed = True
        if changed:
            await session.flush()
        return user, False

    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        is_admin=is_admin,
    )
    session.add(user)
    await session.flush()
    return user, True


async def get_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def set_referrer(
    session: AsyncSession, user: User, referrer_id: int
) -> bool:
    """Attach a referrer to a freshly created user (idempotent / safe)."""
    if user.referrer_id or user.id == referrer_id:
        return False
    referrer = await get_by_id(session, referrer_id)
    if referrer is None:
        return False
    user.referrer_id = referrer_id
    await session.flush()
    return True


async def add_balance(
    session: AsyncSession, user: User, amount: Decimal | int
) -> None:
    user.balance = Decimal(user.balance) + Decimal(amount)
    await session.flush()


async def all_user_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(
        select(User.telegram_id).where(User.is_blocked.is_(False))
    )
    return [row[0] for row in result.all()]


async def user_order_stats(
    session: AsyncSession, user_id: int
) -> tuple[int, Decimal]:
    """Return (orders_count, total_spent) counting non-cancelled orders."""
    result = await session.execute(
        select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_price), 0),
        ).where(
            Order.user_id == user_id,
            Order.status != OrderStatus.cancelled,
        )
    )
    count, total = result.one()
    return int(count), Decimal(total)
