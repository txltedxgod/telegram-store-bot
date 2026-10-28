from decimal import Decimal
from bot.database.models import Category, Product
from bot.keyboards.user import (
    back_home,
    categories_kb,
    language_selection_kb,
    main_menu,
    payment_methods_kb,
    products_kb,
)


def test_language_selection_keyboard():
    kb = language_selection_kb()
    assert kb is not None
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert "🇺🇦 Українська" in button_texts
    assert "🇬🇧 English" in button_texts


def test_main_menu_keyboard_uk():
    kb = main_menu(lang="uk")
    assert kb is not None
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Каталог" in t for t in button_texts)
    assert any("Кошик" in t for t in button_texts)
    assert any("Мої замовлення" in t for t in button_texts)
    assert any("Особистий кабінет" in t for t in button_texts)
    # Check that custom emoji icons are attached to buttons
    assert kb.inline_keyboard[0][0].icon_custom_emoji_id is not None


def test_main_menu_keyboard_en():
    kb = main_menu(lang="en")
    assert kb is not None
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Catalog" in t for t in button_texts)
    assert any("Cart" in t for t in button_texts)
    assert any("My Orders" in t for t in button_texts)
    assert any("Profile" in t for t in button_texts)
    assert kb.inline_keyboard[0][0].icon_custom_emoji_id is not None


def test_payment_methods_keyboard():
    kb = payment_methods_kb(lang="uk")
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Гривня" in t for t in button_texts)
    assert any("Криптовалюта" in t for t in button_texts)
    assert kb.inline_keyboard[0][0].icon_custom_emoji_id is not None


def test_back_home_keyboard():
    kb = back_home(lang="uk")
    assert kb is not None
    assert len(kb.inline_keyboard) == 1
    assert "В меню" in kb.inline_keyboard[0][0].text
    assert kb.inline_keyboard[0][0].icon_custom_emoji_id is not None


def test_categories_keyboard():
    cats = [
        Category(id=1, name="VPN", emoji="🛡"),
        Category(id=2, name="AI", emoji="🤖"),
    ]
    kb = categories_kb(cats, lang="uk")
    assert len(kb.inline_keyboard) == 3  # 2 categories + Back button
    assert "VPN" in kb.inline_keyboard[0][0].text
    assert "AI" in kb.inline_keyboard[1][0].text
    assert kb.inline_keyboard[0][0].icon_custom_emoji_id is not None


def test_products_keyboard():
    products = [
        Product(id=1, name="Shadowsocks", price=Decimal("150.00"), stock=10, is_active=True),
        Product(id=2, name="WireGuard", price=Decimal("200.00"), stock=5, is_active=True),
    ]
    kb = products_kb(products, category_id=1, lang="uk")
    assert len(kb.inline_keyboard) == 3  # 2 products + Back button
    assert "Shadowsocks" in kb.inline_keyboard[0][0].text
    assert "WireGuard" in kb.inline_keyboard[1][0].text
    assert kb.inline_keyboard[0][0].icon_custom_emoji_id is not None
