import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(r"C:\Users\dev\.gemini\antigravity\scratch\telegram-store-bot\.env")
from aiogram import Bot
import bot.utils.emojis as em

sys.stdout.reconfigure(encoding="utf-8")

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = 36038634  # seocry

async def main():
    bot = Bot(token=BOT_TOKEN)
    
    emoji_constants = [attr for attr in dir(em) if attr.startswith("EMOJI_")]
    valid_emojis = {}
    invalid_emojis = {}

    print(f"Testing {len(emoji_constants)} emojis with Bot API...")
    for name in emoji_constants:
        val = getattr(em, name)
        html = f"Testing {name}: <tg-emoji emoji-id=\"{val}\">⭐</tg-emoji>"
        try:
            msg = await bot.send_message(USER_ID, html, parse_mode="HTML")
            await bot.delete_message(USER_ID, msg.message_id)
            valid_emojis[name] = val
            print(f"  [VALID] {name} = '{val}'")
        except Exception as e:
            invalid_emojis[name] = (val, str(e))
            print(f"  [INVALID!] {name} = '{val}' -> {e}")

    print(f"\nSummary: {len(valid_emojis)} valid, {len(invalid_emojis)} invalid")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
