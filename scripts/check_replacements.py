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
    test_ids = {
        "WAVE_Restricted": "5472055112702629499",
        "HAND_tgmacicons": "5258362429389152256",
        "CLAP_tgmacicons": "5258501105293205250",
        "PHONE_Restricted": "5407025283456835913",
        "PHONE_tgmacicons": "5258020476977946656",
        "PROFILE_tgmacicons": "5258362837411045098",
    }
    for name, doc_id in test_ids.items():
        try:
            m = await bot.send_message(USER_ID, f"Test {name}: <tg-emoji emoji-id=\"{doc_id}\">👋</tg-emoji>", parse_mode="HTML")
            await bot.delete_message(USER_ID, m.message_id)
            print(f"[VALID] {name}: {doc_id}")
        except Exception as e:
            print(f"[INVALID] {name}: {doc_id} -> {e}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
