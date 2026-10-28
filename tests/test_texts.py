from decimal import Decimal

from bot.database.models import OrderStatus, Product, User
from bot.utils.texts import money, product_card, status_label, welcome_text


def test_money_formatting():
    assert "2\u202f490 ₽" == money(Decimal("2490.00"))
    assert "0 ₽" == money(0)
    assert "10\u202f000 ₽" == money(10000)


def test_status_label():
    assert "⏳ Ожидает оплаты" in status_label(OrderStatus.pending)
    assert "✅ Успешно выполнен" in status_label(OrderStatus.completed)
    assert "❌ Отменён" in status_label(OrderStatus.cancelled)


def test_welcome_text():
    user = User(
        telegram_id=999,
        full_name="Alice",
        balance=Decimal("500.00"),
    )
    text = welcome_text(user)
    assert "SEO STORE • Цифровой Маркетплейс" in text
    assert "Alice" in text
    assert "500 ₽" in text


def test_product_card():
    product = Product(
        name="GPT-4o Plus (1 мес)",
        description="Персональный доступ к ChatGPT Plus.",
        price=Decimal("1990.00"),
        stock=15,
        is_active=True,
    )
    text = product_card(product)
    assert "GPT-4o Plus" in text
    assert "1\u202f990 ₽" in text
    assert "15 шт." in text
    assert "Персональный доступ" in text
