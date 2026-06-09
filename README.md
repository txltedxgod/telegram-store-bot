# 🛒 Telegram Store Bot

Полнофункциональный коммерческий Telegram-магазин на **aiogram 3** с каталогом,
корзиной, оформлением заказов через FSM, профилем покупателя, админ-панелью,
промокодами, реферальной системой и рассылками. Проект построен по слоистой
архитектуре (handlers → services → database) и запускается одной командой через
Docker Compose.

## ✨ Возможности

### Пользовательская часть

* 🛒 **Каталог** с категориями и фильтрацией товаров
* 🧺 **Корзина**: добавление, изменение количества, удаление, очистка
* ✅ **Оформление заказа** через FSM (контакт → комментарий → подтверждение)
* 📦 **Мои заказы** и история покупок со статусами
* 👤 **Профиль**: баланс, количество заказов, сумма покупок
* ⭐ **Избранное**
* 🔍 **Поиск товаров** по названию
* 🎁 **Реферальная программа** (`/ref`, deep-link `start=ref\_<id>`)
* 🏷 **Промокоды** со скидками

### Админ-панель (`/admin`)

* ➕ Добавление товара (FSM)
* ✏️ Изменение товара (название / цена / описание / остаток)
* ❌ Удаление товара
* 📦 Управление заказами и смена статусов (с уведомлением покупателя)
* 📊 Статистика (пользователи, заказы, оборот, метрики за сегодня)
* 🏆 Рейтинг популярных товаров
* 📢 Массовая рассылка с отчётом
* 🏷 Создание промокодов
* 📄 Экспорт заказов в CSV
* 🔔 Уведомления о новых заказах и низком остатке товара

\---

## 🧱 Стек технологий

|Технология|Назначение|
|-|-|
|**Python 3.12+**|Язык разработки|
|**aiogram 3.28+**|Telegram Bot API 9.4, роутеры, FSM, middlewares, цветные кнопки|
|**SQLAlchemy 2.0 (async)**|ORM, асинхронный доступ к БД|
|**PostgreSQL**|Хранилище данных|
|**asyncpg**|Асинхронный драйвер PostgreSQL|
|**Alembic**|Миграции схемы БД|
|**pydantic-settings**|Типизированная конфигурация из `.env`|
|**Docker / Docker Compose**|Контейнеризация и запуск|

\---

## 🚀 Установка

### 1\. Клонирование

```bash
git clone https://github.com/txltedxgod/telegram-store-bot.git
cd telegram-store-bot
```

### 2\. Настройка окружения

```bash
cp .env.example .env
```

Откройте `.env` и укажите:

* `BOT\_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
* `ADMIN\_IDS` — ваш Telegram ID (узнать можно у [@userinfobot](https://t.me/userinfobot))

\---

## 🐳 Запуск через Docker

Проект поднимается командой:

```bash
docker compose up -d
```

Что произойдёт:

1. Поднимется контейнер PostgreSQL с healthcheck.
2. Контейнер бота дождётся базы, применит миграции (`alembic upgrade head`).
3. При первом старте (если `SEED\_DEMO\_DATA=true`) загрузятся демо-категории и товары.
4. Бот запустится в режиме long-polling.

Логи:

```bash
docker compose logs -f bot
```

Остановка:

```bash
docker compose down          # сохранить данные
docker compose down -v       # удалить данные вместе с томом БД
```

### Локальный запуск без Docker

```bash
python -m venv .venv \&\& source .venv/bin/activate
pip install -r requirements.txt
# Поднимите PostgreSQL и пропишите POSTGRES\_HOST=localhost в .env
alembic upgrade head
python -m bot.bot
```

\---

## 🗄 Схема базы данных

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ CART\_ITEMS : has
    USERS ||--o{ FAVORITES : saves
    USERS ||--o{ USERS : refers
    CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--o{ CART\_ITEMS : in
    PRODUCTS ||--o{ ORDER\_ITEMS : in
    PRODUCTS ||--o{ FAVORITES : in
    ORDERS ||--o{ ORDER\_ITEMS : includes
    PROMOCODES ||--o{ ORDERS : applied\_to

    USERS {
        int id PK
        bigint telegram\_id
        string username
        string full\_name
        numeric balance
        int referrer\_id FK
        bool is\_admin
        bool is\_blocked
        datetime created\_at
    }
    CATEGORIES {
        int id PK
        string name
        string emoji
    }
    PRODUCTS {
        int id PK
        int category\_id FK
        string name
        text description
        numeric price
        int stock
        bool is\_active
        datetime created\_at
    }
    CART\_ITEMS {
        int id PK
        int user\_id FK
        int product\_id FK
        int quantity
    }
    ORDERS {
        int id PK
        int user\_id FK
        enum status
        numeric total\_price
        numeric discount
        string contact
        text comment
        int promocode\_id FK
        datetime created\_at
    }
    ORDER\_ITEMS {
        int id PK
        int order\_id FK
        int product\_id FK
        string product\_name
        int quantity
        numeric price
    }
    PROMOCODES {
        int id PK
        string code
        int discount\_percent
        int max\_uses
        int used\_count
        bool is\_active
    }
    FAVORITES {
        int id PK
        int user\_id FK
        int product\_id FK
    }
```

\---

## 🗂 Структура проекта

```
telegram-store-bot/
├── bot/
│   ├── handlers/        # роутеры: start, catalog, cart, checkout, orders,
│   │                    #          profile, favorites, search, admin
│   ├── keyboards/       # инлайн-клавиатуры и callback-фабрики
│   ├── middlewares/     # сессия БД, логирование, регистрация пользователя
│   ├── services/        # бизнес-логика и доступ к данным (репозитории)
│   ├── database/        # base, engine, models, seed
│   ├── states/          # группы состояний FSM
│   ├── filters/         # IsAdmin и др
│   ├── utils/           # логирование, тексты/форматирование
│   ├── config.py        # настройки из .env
│   └── bot.py           # точка входа
├── alembic/             # миграци
├── docker/              # entrypoint
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md
```

\---

## ⌨️ Примеры команд

|Команда|Описание|
|-|-|
|`/start`|Запуск и главное меню|
|`/start ref\_42`|Запуск по реферальной ссылке (пригласил пользователь #42)|
|`/menu`|Открыть главное меню|
|`/ref`|Получить свою реферальную ссылку|
|`/admin`|Админ-панель (только для `ADMIN\_IDS`)|

\---

## 🧾 Логирование

Каждое действие логируется в stdout (удобно для `docker compose logs`):

```
INFO  | bot.users    | User 456 registered
INFO  | bot.checkout | User 123 created order #15
INFO  | bot.admin    | Admin 999 added product Steam Account
INFO  | bot.admin    | Broadcast finished: success=523 errors=7
```

\---

## 🛣 Возможные улучшения

* Платёжный провайдер (Telegram Payments / ЮKassa / Crypto)
* Redis-хранилище для FSM в проде
* Покрытие тестами (pytest + pytest-asyncio)
* Веб-админка и аналитика

\---

## 📄 Лицензия

MIT — см. файл [LICENSE](LICENSE).

