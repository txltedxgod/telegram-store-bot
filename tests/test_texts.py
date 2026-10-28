from decimal import Decimal

from bot.database.models import OrderStatus, Product, User
from bot.utils.texts import money, product_card, status_label, welcome_text


def test_money_formatting():
    # 2490 / 41.5 = 60.00
    assert "2\u202f490 ₴ ($60.00)" == money(Decimal("2490.00"))
    assert "0 ₴ ($0.00)" == money(0)


def test_status_label():
    assert "⏳ Очікує оплати" in status_label(OrderStatus.pending, "uk")
    assert "✅ Успішно виконано" in status_label(OrderStatus.completed, "uk")
    assert "❌ Скасовано" in status_label(OrderStatus.cancelled, "uk")
    assert "⏳ Pending Payment" in status_label(OrderStatus.pending, "en")


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
