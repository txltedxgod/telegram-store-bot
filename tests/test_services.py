from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Category, Product, Promocode, User
from bot.services import cart as cart_service
from bot.services import categories as categories_service
from bot.services import orders as orders_service
from bot.services import products as products_service
from bot.services import promocodes as promo_service
from bot.services import users as users_service


@pytest.mark.asyncio
async def test_user_creation_and_referral(session: AsyncSession):
    # 1. Create referrer
    referrer, created = await users_service.get_or_create_user(
        session,
        telegram_id=111111,
        username="top_referrer",
        full_name="Top Referrer",
    )
    assert created is True
    assert referrer.telegram_id == 111111
    await session.commit()

    # 2. Create referee
    referee, created = await users_service.get_or_create_user(
        session,
        telegram_id=222222,
        username="new_buyer",
        full_name="New Buyer",
    )
    assert created is True
    await session.commit()

    # 3. Set referrer
    success = await users_service.set_referrer(session, referee, referrer.id)
    assert success is True
    await session.commit()

    # Refresh
    refreshed_referee = await users_service.get_by_telegram_id(session, 222222)
    assert refreshed_referee.referrer_id == referrer.id

    # Add balance bonus
    await users_service.add_balance(session, referrer, Decimal("50.00"))
    await session.commit()
    refreshed_referrer = await users_service.get_by_telegram_id(session, 111111)
    assert refreshed_referrer.balance == Decimal("50.00")


@pytest.mark.asyncio
async def test_cart_and_order_flow(
    session: AsyncSession,
    sample_user: User,
    sample_category: Category,
    sample_product: Product,
    sample_promocode: Promocode,
):
    # 1. Add product to cart
    item = await cart_service.add_item(session, sample_user.id, sample_product.id, quantity=2)
    await session.commit()
    assert item.quantity == 2

    # 2. Get items and verify total
    items = await cart_service.get_items(session, sample_user.id)
    assert len(items) == 1
    total = cart_service.total(items)
    # 2490 * 2 = 4980
    assert total == Decimal("4980.00")

    # 3. Checkout with promocode (20% discount)
    promo = await promo_service.get_active(session, "TEST20")
    assert promo is not None

    order = await orders_service.create_from_cart(
        session,
        user_id=sample_user.id,
        contact="@testbuyer",
        comment="Auto-delivery please",
        promocode=promo,
    )
    await session.commit()

    assert order.id is not None
    # 20% of 4980 = 996. Total = 4980 - 996 = 3984
    assert order.discount == Decimal("996")
    assert order.total_price == Decimal("3984.00")

    # Cart should be empty after checkout
    items_after = await cart_service.get_items(session, sample_user.id)
    assert len(items_after) == 0


@pytest.mark.asyncio
async def test_insufficient_stock_error(
    session: AsyncSession,
    sample_user: User,
    sample_product: Product,
):
    # Try adding more than stock (stock is 50)
    await cart_service.add_item(session, sample_user.id, sample_product.id, quantity=100)
    await session.commit()

    with pytest.raises(orders_service.CheckoutError, match="Недостаточно товара"):
        await orders_service.create_from_cart(
            session,
            user_id=sample_user.id,
            contact="@buyer",
            comment="",
        )
