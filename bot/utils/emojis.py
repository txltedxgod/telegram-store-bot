"""Custom Premium Emojis extracted from verified Telegram Custom Emoji packs."""
from __future__ import annotations

# Verified Custom Emoji Document IDs (tgmacicons, FinanceEmoji, RestrictedEmoji, pk_1703898_by_EmojiRuBot)
EMOJI_WAVE = "5472055112702629499"         # 👋 Waving hand (Animated Telegram Emoji)
EMOJI_ARROW_DOWN = "5258336354642697821"   # ⬇️ Down arrow
EMOJI_STORE = "5361862942130220421"        # 🛍 Storefront
EMOJI_LIGHTNING = "5258152182150077732"    # ⚡️ Lightning / Flash
EMOJI_STAR = "5258185631355378853"         # ⭐️ Star / Telegram Premium
EMOJI_COIN = "5258368777350816286"         # 🪙 Coin / Crypto / Balance
EMOJI_PROFILE = "5258362837411045098"      # 👤 User Profile
EMOJI_ROBOT = "5258093637450866522"        # 🤖 AI / Neural
EMOJI_CATALOG = "5258514780469075716"      # 📂 Catalog / Folder
EMOJI_CHECK = "5260726538302660868"        # ✅ Checkmark / Verified
EMOJI_CROSS = "5258226313285607065"        # ❌ Cancel / Cross
EMOJI_GIFT = "6032937473162614352"         # 🎁 Referral Gift
EMOJI_LOCK = "5258476306152038031"         # 🔒 Security Lock
EMOJI_CART = "5258514780469075716"         # 🧺 Cart
EMOJI_ORDERS = "5258134813302332906"       # 📦 Orders Box
EMOJI_SEARCH = "5429571366384842791"       # 🔎 Search Lens
EMOJI_LANGUAGE = "5879585266426973039"     # 🌐 Globe / Language
EMOJI_KEY = "6005570495603282482"          # 🔑 Software Keys
EMOJI_SHIELD = "5926783847453692661"       # 🛡 VPN / Security
EMOJI_GAME = "5258508428212445001"         # 🎮 Games / Steam
EMOJI_CARD = "5967548335542767952"         # 💳 Bank Card
EMOJI_CHART = "5258391025281408576"        # 📊 Chart / Status
EMOJI_CALENDAR = "5258105663359294787"     # 📅 Calendar / Date
EMOJI_PENDING = "5258419835922030550"      # ⏳ / 🕔 Pending Clock
EMOJI_PHONE = "5258020476977946656"        # 📞 Phone / Contact
EMOJI_ID = "5334685089160783060"           # 🆔 / 🪪 ID Card / Badge
EMOJI_MOBILE = "5407025283456835913"       # 📱 Mobile / Username (Animated Telegram Emoji)
EMOJI_MONEY = "5258204546391351475"        # 💸 Money / Total Spent
EMOJI_TAG = "5296348778012361146"          # 🏷 Promo Tag
EMOJI_CHAT = "5258215846450305872"         # 💬 Comment / Chat
EMOJI_INFO = "5258503720928288433"         # ℹ️ Info / Warning
EMOJI_DIAMOND = "5280962371207077415"      # 💎 Diamond
EMOJI_UA = "5447309366568953338"           # 🇺🇦 Ukraine Flag (RestrictedEmoji - same pack as Britain)
EMOJI_UK = "5202196682497859879"           # 🇬🇧 UK Flag (RestrictedEmoji)
EMOJI_CHAIN = "5260730055880876557"        # 🔗 / ⛓ Link / Chain


def ce(emoji_id: str, fallback: str) -> str:
    """Format Telegram custom emoji tag for HTML parse_mode."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
