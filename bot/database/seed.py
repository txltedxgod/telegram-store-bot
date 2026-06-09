"""Optional demo data so a fresh deployment looks like a real store."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import categories as categories_service
from bot.services import products as products_service
from bot.services import promocodes as promocodes_service

DEMO_CATEGORIES = [
    ("Софт", "💻"),
    ("Игры", "🎮"),
    ("Аккаунты", "📱"),
]

# (name, description, price, stock)
DEMO_PRODUCTS = {
    "Софт": [
        (
            "Windows 11 Pro",
            "Бессрочный лицензионный ключ активации. Привязывается к аккаунту Microsoft, "
            "подходит для чистой установки и обновления.",
            Decimal("450"),
            30,
        ),
        (
            "Microsoft Office 365 (1 год)",
            "Подписка на 12 месяцев: Word, Excel, PowerPoint, Outlook + 1 ТБ OneDrive.",
            Decimal("600"),
            18,
        ),
        (
            "Kaspersky Plus (1 год)",
            "Антивирус на 3 устройства: защита в реальном времени, VPN и менеджер паролей.",
            Decimal("350"),
            25,
        ),
        (
            "VPN Premium (12 мес)",
            "Безлимитный трафик, серверы в 30+ странах, до 5 устройств одновременно.",
            Decimal("300"),
            60,
        ),
    ],
    "Игры": [
        (
            "Cyberpunk 2077 (Steam)",
            "Цифровая копия игры для Steam. Регион RU/CIS, активация по ключу.",
            Decimal("1200"),
            8,
        ),
        (
            "GTA V: Premium Edition",
            "Основная игра + GTA Online и пакет быстрого старта.",
            Decimal("900"),
            5,
        ),
        (
            "Minecraft (Java + Bedrock)",
            "Лицензионный аккаунт с полным доступом к обеим версиям игры.",
            Decimal("150"),
            50,
        ),
        (
            "Пополнение Steam на 500 ₽",
            "Зачисление 500 ₽ на кошелёк Steam по логину. Зачисление до 15 минут.",
            Decimal("550"),
            100,
        ),
        (
            "Game Pass Ultimate (1 мес)",
            "Доступ к 400+ игр на PC и Xbox + EA Play на 30 дней.",
            Decimal("250"),
            3,
        ),
    ],
    "Аккаунты": [
        (
            "Steam аккаунт (с почтой)",
            "Новый аккаунт с привязанной почтой. Полный доступ и смена данных.",
            Decimal("100"),
            15,
        ),
        (
            "Spotify Premium (3 мес)",
            "Музыка без рекламы, офлайн-режим и высокое качество звука.",
            Decimal("250"),
            40,
        ),
        (
            "YouTube Premium (1 год)",
            "Без рекламы, фоновое воспроизведение и YouTube Music на 12 месяцев.",
            Decimal("300"),
            22,
        ),
        (
            "Telegram Premium (1 год)",
            "Расширенные лимиты, эксклюзивные стикеры и реакции, без рекламы.",
            Decimal("1500"),
            12,
        ),
        (
            "Discord Nitro (1 мес)",
            "Бусты сервера, HD-стримы, большие загрузки и кастомный профиль.",
            Decimal("200"),
            2,
        ),
    ],
}

# (code, discount_percent, max_uses) — max_uses=0 означает «без лимита»
DEMO_PROMOCODES = [
    ("WELCOME10", 10, 0),
    ("SALE25", 25, 100),
]


async def seed_demo_data(session: AsyncSession) -> bool:
    """Populate demo data only if the catalog is empty. Returns True if seeded."""
    existing = await categories_service.list_categories(session)
    if existing:
        return False

    for name, emoji in DEMO_CATEGORIES:
        category = await categories_service.get_or_create_category(session, name, emoji)
        for p_name, p_desc, price, stock in DEMO_PRODUCTS.get(name, []):
            await products_service.create_product(
                session,
                name=p_name,
                price=price,
                description=p_desc,
                category_id=category.id,
                stock=stock,
            )

    for code, discount, max_uses in DEMO_PROMOCODES:
        if not await promocodes_service.get_by_code(session, code):
            await promocodes_service.create(
                session, code=code, discount_percent=discount, max_uses=max_uses
            )
    return True
