"""Optional demo data so a fresh deployment looks like a real store."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import categories as categories_service
from bot.services import products as products_service
from bot.services import promocodes as promocodes_service

DEMO_CATEGORIES = [
    ("⚡️ Подписки & Premium", "💎"),
    ("🤖 AI & Нейросети", "🧠"),
    ("💻 Софт & Лицензии", "🔑"),
    ("🛡 Безопасность & VPN", "🌐"),
    ("🕹 Игры & Steam", "🎮"),
]

# (name, description, price, stock)
DEMO_PRODUCTS = {
    "⚡️ Подписки & Premium": [
        (
            "⭐️ Telegram Premium (12 мес)",
            "Лицензионная подписка Telegram Premium на 1 год.\n\n"
            "• Активация без входа в аккаунт (Gift-ссылка / по @username)\n"
            "• Лимиты x2 (до 4 ГБ файлы, 1000 каналов)\n"
            "• Максимальная скорость загрузки медиа\n"
            "• Расшифровка голосовых и видеосообщений в текст\n"
            "• Эксклюзивные стикеры, кастомные эмодзи и статус в профиле",
            Decimal("2490"),
            50,
        ),
        (
            "⭐️ Telegram Premium (3 мес)",
            "Лицензионная подписка Telegram Premium на 3 месяца.\n\n"
            "• Моментальная активация по логину\n"
            "• Все преимущества и премиум функции Telegram без переплат",
            Decimal("790"),
            35,
        ),
        (
            "🔮 Discord Nitro (1 мес + 2 буста)",
            "Полная подписка Discord Nitro на 30 дней.\n\n"
            "• 2 бесплатных буста для вашего сервера\n"
            "• Пользовательские эмодзи и стикеры на любых серверах\n"
            "• Стримы в высоком разрешении (HD 1080p/60fps и 4K)\n"
            "• Анимированный аватар и кастомный баннер профиля",
            Decimal("390"),
            40,
        ),
        (
            "🎧 Spotify Premium (12 мес)",
            "Индивидуальная подписка Spotify на 12 месяцев на ваш личный аккаунт.\n\n"
            "• Премиальное качество звука (Very High 320 kbps)\n"
            "• Полное отсутствие аудио- и баннерной рекламы\n"
            "• Офлайн-режим и скачивание треков в память устройства",
            Decimal("1190"),
            25,
        ),
        (
            "🎬 YouTube Premium (12 мес)",
            "Подписка YouTube Premium + YouTube Music на 1 год.\n\n"
            "• Просмотр видео без рекламы на Smart TV, смартфоне и ПК\n"
            "• Фоновое воспроизведение при заблокированном экране\n"
            "• Доступ к библиотеке YouTube Music без ограничений",
            Decimal("1490"),
            20,
        ),
    ],
    "🤖 AI & Нейросети": [
        (
            "🧠 ChatGPT Plus (GPT-4o + o1-preview)",
            "Подписка ChatGPT Plus на 1 месяц.\n\n"
            "• Доступ к моделям GPT-4o, GPT-4o-mini и рассуждающим моделям OpenAI o1\n"
            "• Генератор изображений DALL-E 3 и продвинутый анализ данных (Code Interpreter)\n"
            "• Персональный аккаунт с гарантией на весь оплаченный период",
            Decimal("1890"),
            15,
        ),
        (
            "💎 Claude Pro (Opus & Sonnet 3.5)",
            "Подписка Claude Pro от Anthropic на 30 дней.\n\n"
            "• Лимиты x5 на топовую модель Claude 3.5 Sonnet\n"
            "• Превосходный анализ кода, архитектуры и длинных документов (200k контекст)\n"
            "• Интерактивная среда Artifacts для рендеринга кода и UI",
            Decimal("1950"),
            12,
        ),
        (
            "🎨 Midjourney v6.1 (Standard Plan)",
            "Доступ к генеративной нейросети Midjourney на 1 месяц.\n\n"
            "• 15 часов быстрой генерации (Fast GPU)\n"
            "• Неограниченная генерация в Relax-режиме\n"
            "• Фотореалистичное качество артов, рендеров и концептов",
            Decimal("1650"),
            10,
        ),
    ],
    "💻 Софт & Лицензии": [
        (
            "🔑 Windows 11 Pro (Retail Key)",
            "Бессрочный лицензионный ключ активации Windows 11 Pro.\n\n"
            "• Официальная онлайн-активация на серверах Microsoft\n"
            "• Пожизненная цифровая лицензия (привязка к железу)\n"
            "• Поддержка BitLocker, удаленного рабочего стола и Hyper-V\n"
            "• Все языки и разрядности (x64 / ARM64)",
            Decimal("490"),
            100,
        ),
        (
            "📑 Microsoft Office 365 (1 год)",
            "Подписка на офисный пакет Office 365 на 12 месяцев.\n\n"
            "• Приложения Word, Excel, PowerPoint, Outlook, OneNote\n"
            "• 1 ТБ облачного хранилища OneDrive\n"
            "• Установка на 5 устройств (ПК, Mac, планшет, телефон)",
            Decimal("790"),
            30,
        ),
        (
            "⚡️ JetBrains All Products Pack (1 год)",
            "Лицензия на весь пакет сред разработки JetBrains на 1 год.\n\n"
            "• Включает PyCharm, IntelliJ IDEA, CLion, GoLand, WebStorm, RustRover\n"
            "• Официальная подписка с автообновлением плагинов и IDE",
            Decimal("2990"),
            8,
        ),
    ],
    "🛡 Безопасность & VPN": [
        (
            "🌐 VLESS / Reality VPN (Ultra Fast 12 мес)",
            "Премиальный скоростной VPN на протоколах нового поколения VLESS / Reality.\n\n"
            "• Скорость до 1 Гбит/с, минимальный пинг (<20 ms)\n"
            "• Полная невидимость для DPI и систем блокировок\n"
            "• 5 серверов: Германия, Нидерланды, Швеция, США, Сингапур\n"
            "• Поддержка v2rayN, V2Box, Streisand, Nekobox на iOS/Android/Windows/macOS",
            Decimal("890"),
            100,
        ),
        (
            "🛡 AdGuard Premium (Вечная лицензия)",
            "Пожизненная лицензия блокировщика рекламы AdGuard.\n\n"
            "• Блокировка рекламы, баннеров, трекеров и майнеров\n"
            "• Защита от фишинга и вредоносных сайтов\n"
            "• Активация на 3 устройствах (Windows, Mac, Android, iOS)",
            Decimal("550"),
            25,
        ),
    ],
    "🕹 Игры & Steam": [
        (
            "💳 Пополнение баланса Steam (500 ₽)",
            "Мгновенное пополнение кошелька Steam по логину аккаунта.\n\n"
            "• Регионы: Россия, Казахстан, СНГ\n"
            "• Зачисление средств за 1–3 минуты\n"
            "• Без передачи пароля — требуется только логин аккаунта",
            Decimal("550"),
            100,
        ),
        (
            "🏙 Cyberpunk 2077: Phantom Liberty",
            "Цифровое издание игры + масштабное сюжетное дополнение для Steam.\n\n"
            "• Лицензионный ключ активации\n"
            "• Доступ ко всем обновлениям и патчу 2.1+",
            Decimal("1690"),
            15,
        ),
        (
            "🚗 GTA V: Premium Edition (PC)",
            "Основная игра Grand Theft Auto V + GTA Online.\n\n"
            "• Стартовый набор «Преступная организация» (1 млн $ в игре + недвижимость)\n"
            "• Лицензионный ключ для активации в Rockstar Games Launcher / Steam",
            Decimal("990"),
            20,
        ),
    ],
}

# (code, discount_percent, max_uses)
DEMO_PROMOCODES = [
    ("WELCOME10", 10, 0),
    ("VIP20", 20, 50),
    ("SPRING15", 15, 100),
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
