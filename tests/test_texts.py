from decimal import Decimal

from bot.database.models import OrderStatus, Product, User
from bot.utils.texts import money, product_card, status_label, welcome_text


def test_money_formatting():
    # 2490 / 41.5 = 60.00
    assert "2\u202f490 ₴ ($60.00)" == money(Decimal("2490.00"))
    assert "0 ₴ ($0.00)" == money(0)


def test_status_label():
    label_uk = status_label(OrderStatus.pending, "uk")
    assert "Очікує оплати" in label_uk
    assert "<tg-emoji" in label_uk
    assert "Успішно виконано" in status_label(OrderStatus.completed, "uk")
    assert "Скасовано" in status_label(OrderStatus.cancelled, "uk")
    assert "Pending Payment" in status_label(OrderStatus.pending, "en")


def test_welcome_text_uk():
    user = User(
        telegram_id=999,
        full_name="Alice",
        language_code="uk",
        balance=Decimal("500.00"),
    )
    text = welcome_text(user)
    assert "SEO Store" in text
    assert "Alice" in text
    assert "500 ₴" in text


def test_welcome_text_en():
    user = User(
        telegram_id=999,
        full_name="Bob",
        language_code="en",
        balance=Decimal("1000.00"),
    )
    text = welcome_text(user)
    assert "SEO Store" in text
    assert "Bob" in text
    assert "1\u202f000 ₴" in text


def test_product_card():
    product = Product(
        name="ChatGPT Plus (1 міс)",
        description="Персональний доступ до GPT-4o.",
        price=Decimal("850.00"),
        stock=15,
        is_active=True,
    )
    text = product_card(product)
    assert "ChatGPT Plus" in text
    assert "850 ₴" in text
    assert "15 шт." in text
    assert "Персональний доступ" in text
    assert "<tg-emoji" in text


def test_profile_text_custom_emojis():
    from bot.utils.texts import profile_text
    user = User(
        telegram_id=123456789,
        username="seocry",
        language_code="uk",
        balance=Decimal("250.00"),
    )
    text = profile_text(user, orders_count=3, total_spent=Decimal("1500.00"))
    assert "123456789" in text
    assert "@seocry" in text
    assert "250 ₴" in text
    assert "1\u202f500 ₴" in text
    assert "<tg-emoji" in text


def test_order_card_custom_emojis():
    from bot.database.models import Order, OrderItem
    from bot.utils.texts import order_card
    order = Order(
        id=42,
        user_id=1,
        total_price=Decimal("999.00"),
        status=OrderStatus.pending,
        payment_method="Картка Monobank",
        contact="@seocry",
        comment="Fast delivery please",
    )
    order.items = [
        OrderItem(
            order_id=42,
            product_id=1,
            product_name="Telegram Premium (12 міс)",
            price=Decimal("999.00"),
            quantity=1,
        )
    ]
    text = order_card(order)
    assert "Замовлення #42" in text
    assert "Telegram Premium" in text
    assert "<tg-emoji" in text
    assert "Monobank" in text

