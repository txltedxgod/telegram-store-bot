"""Custom Premium Emojis extracted from user's Telegram Premium session."""
from __future__ import annotations

# Verified Custom Emoji Document IDs from user's session
EMOJI_STORE = "5361862942130220421"      # 🛍 Storefront
EMOJI_LIGHTNING = "5258152182150077732"  # ⚡️ Lightning / Flash
EMOJI_STAR = "5258185631355378853"       # ⭐️ Star / Diamond
EMOJI_COIN = "5258368777350816286"       # 🪙 Coin / Crypto
EMOJI_PROFILE = "5258362837411045098"    # 👤 User Profile
EMOJI_ROBOT = "5258093637450866522"      # 🤖 AI / Neural
EMOJI_CATALOG = "5258514780469075716"    # 📂 Catalog / Folder
EMOJI_CHECK = "5260726538302660868"      # ✅ Checkmark / Verified
EMOJI_GIFT = "6032937473162614352"       # 🎁 Referral Gift
EMOJI_LOCK = "5260730055880876557"       # 🔒 Security Lock
EMOJI_CART = "5258514780469075716"       # 🧺 Cart
EMOJI_ORDERS = "5258134813302332906"     # 📦 Orders Box
EMOJI_SEARCH = "5429571366384842791"     # 🔎 Search Lens
EMOJI_LANGUAGE = "5879585266426973039"   # 🌐 Globe
EMOJI_KEY = "6005570495603282482"        # 🔑 Software Keys
EMOJI_SHIELD = "5926783847453692661"     # 🛡 VPN / Security
EMOJI_GAME = "5258508428212445001"       # 🎮 Games / Steam
EMOJI_CARD = "5967548335542767952"       # 💳 Bank Card

def ce(emoji_id: str, fallback: str) -> str:
    """Format Telegram custom emoji tag for HTML parse_mode."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
