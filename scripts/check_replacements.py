import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(r"C:\Users\dev\.gemini\antigravity\scratch\telegram-store-bot\.env")
from aiogram import Bot

sys.stdout.reconfigure(encoding="utf-8")

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = 36038634

async def main():
    bot = Bot(token=BOT_TOKEN)
    ua_doc = "5447309366568953338"  # RestrictedEmoji UA
    uk_doc = "5202196682497859879"  # RestrictedEmoji UK
    try:
        m = await bot.send_message(USER_ID, f"Test: <tg-emoji emoji-id=\"{ua_doc}\">🇺🇦</tg-emoji> and <tg-emoji emoji-id=\"{uk_doc}\">🇬🇧</tg-emoji>", parse_mode="HTML")
        await bot.delete_message(USER_ID, m.message_id)
        print(f"[VALID] Both from RestrictedEmoji! UA: {ua_doc}, UK: {uk_doc}")
    except Exception as e:
        print(f"[INVALID] {e}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
