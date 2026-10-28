"""Seed catalog data with Ukrainian and English descriptions, UAH and USD pricing."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import categories as categories_service
from bot.services import products as products_service
from bot.services import promocodes as promocodes_service

DEMO_CATEGORIES = [
    ("Підписки & Premium", "💎"),
    ("AI & Нейромережі", "🧠"),
    ("Софт & Ліцензії", "🔑"),
    ("Безпека & VPN", "🌐"),
    ("Ігри & Steam", "🎮"),
]

# (name, description, price_uah, stock)
DEMO_PRODUCTS = {
    "Підписки & Premium": [
        (
            "Telegram Premium (12 міс)",
            "Ліцензійна підписка Telegram Premium на 1 рік / 1 Year.\n\n"
            "• Активація без входу в акаунт (Gift-посилання / по @username)\n"
            "• Ліміти x2 (файли до 4 ГБ, 1000 каналів, 30 папок)\n"
            "• Максимальна швидкість завантаження медіа\n"
            "• Розпізнавання голосових та відеоповідомлень у текст\n"
            "• Ексклюзивні анімовані стікери, реакції та преміум-статус",
            Decimal("1150"),
            50,
        ),
        (
            "Telegram Premium (3 міс)",
            "Ліцензійна підписка Telegram Premium на 3 місяці.\n\n"
            "• Моментальна активація за юзернеймом\n"
            "• Усі переваги Telegram Premium без переплат",
            Decimal("390"),
            35,
        ),
        (
            "Discord Nitro (1 міс + 2 бусти)",
            "Повна підписка Discord Nitro на 30 днів.\n\n"
            "• 2 безкоштовні бусти для вашого сервера\n"
            "• Користувацькі емодзі та стікери на будь-яких серверах\n"
            "• Стріми у високій роздільній здатності (HD 1080p/60fps та 4K)\n"
            "• Анімований аватар та персональний банер профілю",
            Decimal("190"),
            40,
        ),
        (
            "Spotify Premium (12 міс)",
            "Індивідуальна підписка Spotify на 12 місяців на ваш особистий акаунт.\n\n"
            "• Преміальна якість звуку (Very High 320 kbps)\n"
            "• Повна відсутність аудіо- та банерної реклами\n"
            "• Офлайн-режим та завантаження треків у пам'ять пристрою",
            Decimal("490"),
            25,
        ),
        (
            "YouTube Premium (12 міс)",
            "YouTube Premium + YouTube Music на 1 рік без реклами.\n\n"
            "• Фонове відтворення на мобільних пристроях\n"
            "• Завантаження відео у максимальній якості офлайн\n"
            "• Підключення до вашого існуючого Google-акаунту",
            Decimal("690"),
            30,
        ),
    ],
    "AI & Нейромережі": [
        (
            "ChatGPT Plus (GPT-4o & o1) • 1 міс",
            "Персональна підписка ChatGPT Plus від OpenAI на 30 днів.\n\n"
            "• Доступ до флагманських моделей GPT-4o, GPT-4, o1-preview\n"
            "• Генерація фотографій та ілюстрацій через DALL-E 3\n"
            "• Web Browsing, Code Interpreter та створення власних Custom GPTs\n"
            "• Пріоритетний швидкий відгук у часи пікового навантаження",
            Decimal("850"),
            30,
        ),
        (
            "Midjourney Pro (1 міс)",
            "Офіційна підписка Midjourney Standard/Pro для генерації арту.\n\n"
            "• Необмежена генерація у режимі Relax Mode\n"
            "• 15-30 годин швидкої Fast GPU генерації\n"
            "• Комерційні права на всі згенеровані зображення",
            Decimal("990"),
            15,
        ),
        (
            "Claude Pro / Anthropic (1 міс)",
            "Підписка Claude Pro з доступом до Claude 3.5 Sonnet & Opus.\n\n"
            "• Збільшений контекст (до 200k токенів)\n"
            "• Інтелектуальний аналіз великих кодових баз та документів\n"
            "• Швидкий пріоритетний доступ 24/7",
            Decimal("850"),
            20,
        ),
    ],
    "Софт & Ліцензії": [
        (
            "Windows 11 Pro OEM Key",
            "Оригінальний цифровий ліцензійний ключ активації Windows 11 Pro.\n\n"
            "• Довічна прив'язка до материнської плати ПК\n"
            "• Офіційна онлайн-активація через сервери Microsoft\n"
            "• Підтримка BitLocker, Remote Desktop та віртуалізації Hyper-V",
            Decimal("290"),
            100,
        ),
        (
            "Microsoft Office 365 (1 рік)",
            "Ліцензія Office 365 (Word, Excel, PowerPoint, Outlook) + 1 TB OneDrive.\n\n"
            "• Підключення до 5 пристроїв одночасно (PC, Mac, iPhone, Android)\n"
            "• Повні останні оновлення всіх застосунків пакета",
            Decimal("490"),
            45,
        ),
        (
            "JetBrains All Products Pack (1 рік)",
            "Офіційна підписка на всі IDE від JetBrains на 1 рік.\n\n"
            "• IntelliJ IDEA Ultimate, PyCharm Pro, WebStorm, GoLand, CLion, RustRover\n"
            "• Підключення через офіційний JetBrains Account",
            Decimal("1450"),
            12,
        ),
    ],
    "Безпека & VPN": [
        (
            "Shadowsocks Private VPN (3 міс)",
            "Надшвидкий приватний VPN за протоколом Shadowsocks / Vless.\n\n"
            "• Обхід будь-яких блокувань та DPI\n"
            "• Швидкість до 1 Гбіт/с, локації: Франкфурт, Варшава, Амстердам\n"
            "• Підтримка клієнтів Outline, v2ray, Clash, Shadowrocket (iOS/Android/PC)",
            Decimal("190"),
            80,
        ),
        (
            "WireGuard Dedicated VPN (1 рік)",
            "Виділений персональний WireGuard сервер на 12 місяців.\n\n"
            "• Персональна статична IPv4-адреса\n"
            "• Повний No-Logs (відсутність логів та відстеження)\n"
            "• Конфіг за 1 клік у застосунку WireGuard",
            Decimal("490"),
            40,
        ),
        (
            "AdGuard Premium (Вічна ліцензія)",
            "Оригінальний ключ AdGuard Premium для блокування реклами та трекерів.\n\n"
            "• Блокування будь-якої реклами, спливаючих вікон та фішингу\n"
            "• Безстрокова ліцензія на 3 пристрої",
            Decimal("350"),
            35,
        ),
    ],
    "Ігри & Steam": [
        (
            "Steam Gift Card 500 ₴",
            "Офіційна карта поповнення гаманця Steam на 500 UAH.\n\n"
            "• Моментальна видача 16-значного цифрового пін-коду\n"
            "• Для українських та європейських регіонів Steam",
            Decimal("490"),
            60,
        ),
        (
            "Steam Gift Card $25 USD",
            "Карта поповнення гаманця Steam на $25 USD.\n\n"
            "• Пряме зарахування на баланс акаунта\n"
            "• Моментальна автоматична видача",
            Decimal("1035"),
            45,
        ),
        (
            "Cyberpunk 2077: Phantom Liberty",
            "Ліцензійний ключ активації доповнення Phantom Liberty у Steam.\n\n"
            "• Глобальний цифровий ключ (Global / Region Free)\n"
            "• Активація безпосередньо у вашому клієнті Steam",
            Decimal("790"),
            20,
        ),
    ],
}

DEMO_PROMOCODES = [
    ("WELCOME10", 10, 100),
    ("VIP20", 20, 50),
    ("SPRING15", 15, 75),
]


async def seed_demo_data(session: AsyncSession) -> None:
    """Populate database with bilingual categories and items priced in UAH / USD."""
    existing_categories = await categories_service.get_all(session)
    for cat in existing_categories:
        clean = cat.name.lstrip("⚡️💎🧠🤖🔑💻🌐🛡🎮🕹 ").strip()
        if clean != cat.name:
            cat.name = clean

    all_prods = await products_service.list_all(session)
    for p in all_prods:
        clean = p.name.lstrip("⭐️⭐🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").replace("—", "•").strip()
        if clean != p.name:
            p.name = clean

    existing_by_name = {c.name: c for c in existing_categories}

    for cat_name, emoji in DEMO_CATEGORIES:
        category = existing_by_name.get(cat_name)
        if category is None:
            category = await categories_service.create(session, name=cat_name, emoji=emoji)
            existing_by_name[cat_name] = category

        # Seed products
        for prod_name, desc, price, stock in DEMO_PRODUCTS.get(cat_name, []):
            existing_product = await products_service.get_by_name_and_category(
                session, prod_name, category.id
            )
            if existing_product is None:
                await products_service.create(
                    session,
                    category_id=category.id,
                    name=prod_name,
                    description=desc,
                    price=price,
                    stock=stock,
                )

    # Seed promo codes
    for code, discount, max_uses in DEMO_PROMOCODES:
        if not await promocodes_service.get_by_code(session, code):
            await promocodes_service.create(
                session, code=code, discount_percent=discount, max_uses=max_uses
            )

    await session.commit()
