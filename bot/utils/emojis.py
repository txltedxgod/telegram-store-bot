"""Custom Premium Emojis extracted from the user's Telegram Premium session."""
from __future__ import annotations

# Custom emoji document IDs from user's account (tgmacicons, AethelStore, StatusPack)
EMOJI_STORE = "5361862942130220421"      # 🛍 Storefront
EMOJI_LIGHTNING = "5258152182150077732"  # ⚡️ Lightning / Flash
EMOJI_STAR = "5258185631355378853"       # ⭐️ Premium Star
EMOJI_COIN = "5258368777350816286"       # 🪙 Coin / Crypto
EMOJI_PROFILE = "5258362837411045098"    # 👤 User Profile
EMOJI_ROBOT = "5258093637450866522"      # 🤖 AI / Bot
EMOJI_CATALOG = "5258514780469075716"    # 📂 Catalog
EMOJI_CHECK = "5260726538302660868"      # ✅ Verified
EMOJI_GIFT = "6032937473162614352"       # 🎁 Referral Gift
EMOJI_LOCK = "5260730055880876557"       # 🔒 Security

def ce(emoji_id: str, fallback: str) -> str:
    """Format Telegram custom emoji tag with standard fallback."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
