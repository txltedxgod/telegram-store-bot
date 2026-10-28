import asyncio
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.database.base import Base
from bot.database.models import Category, Product, Promocode, User


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as sess:
        yield sess

    await engine.dispose()


@pytest_asyncio.fixture
async def sample_user(session: AsyncSession) -> User:
    user = User(
        telegram_id=123456789,
        username="testbuyer",
        full_name="Test Buyer",
        balance=Decimal("1000.00"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_category(session: AsyncSession) -> Category:
    cat = Category(
        name="⚡️ Подписки & Premium",
        emoji="⚡️",
    )
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat


@pytest_asyncio.fixture
async def sample_product(session: AsyncSession, sample_category: Category) -> Product:
    prod = Product(
        category_id=sample_category.id,
        name="⭐️ Telegram Premium (12 мес)",
        description="Лицензионная подписка на 1 год без входа в аккаунт.",
        price=Decimal("2490.00"),
        stock=50,
        is_active=True,
    )
    session.add(prod)
    await session.commit()
    await session.refresh(prod)
    return prod


@pytest_asyncio.fixture
async def sample_promocode(session: AsyncSession) -> Promocode:
    promo = Promocode(
        code="TEST20",
        discount_percent=20,
        max_uses=10,
        used_count=0,
    )
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    return promo
