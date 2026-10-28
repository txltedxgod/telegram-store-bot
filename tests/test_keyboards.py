from decimal import Decimal
from bot.database.models import Category, Product
from bot.keyboards.user import back_home, categories_kb, main_menu, products_kb


def test_main_menu_keyboard():
    kb = main_menu()
    assert kb is not None
    # Check that key buttons are present
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Каталог" in t for t in button_texts)
    assert any("Корзина" in t for t in button_texts)
    assert any("Мои заказы" in t for t in button_texts)
    assert any("Личный кабинет" in t for t in button_texts)


def test_back_home_keyboard():
    kb = back_home()
    assert kb is not None
    assert len(kb.inline_keyboard) == 1
    assert "В меню" in kb.inline_keyboard[0][0].text


def test_categories_keyboard():
    cats = [
        Category(id=1, name="VPN", emoji="🛡"),
        Category(id=2, name="AI", emoji="🤖"),
    ]
    kb = categories_kb(cats)
    assert len(kb.inline_keyboard) == 3  # 2 categories + Back button
    assert "🛡 VPN" in kb.inline_keyboard[0][0].text
    assert "🤖 AI" in kb.inline_keyboard[1][0].text


def test_products_keyboard():
    products = [
        Product(id=1, name="Shadowsocks", price=Decimal("150.00"), stock=10, is_active=True),
        Product(id=2, name="WireGuard", price=Decimal("200.00"), stock=5, is_active=True),
    ]
    kb = products_kb(products, category_id=1)
    assert len(kb.inline_keyboard) == 3  # 2 products + Back button
    assert "Shadowsocks" in kb.inline_keyboard[0][0].text
    assert "WireGuard" in kb.inline_keyboard[1][0].text
