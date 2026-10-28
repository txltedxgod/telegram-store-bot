import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(r"C:\Users\dev\.gemini\antigravity\scratch\tg_assistant\.env")
from telethon import TelegramClient
from telethon.tl.types import MessageEntityCustomEmoji

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

sys.stdout.reconfigure(encoding="utf-8")

BOT_USERNAME = "seostrbot"

async def main():
    session_path = r"C:\Users\dev\.gemini\antigravity\scratch\tg_assistant\my_userbot"
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    await client.send_message(BOT_USERNAME, "/start")
    await asyncio.sleep(2.0)

    msg = (await client.get_messages(BOT_USERNAME, limit=1))[0]
    orders_btn = None
    for row in msg.buttons or []:
        for b in row:
            if "замовлення" in b.text.lower() or "orders" in b.text.lower():
                orders_btn = b
                break

    if orders_btn:
        print(f"Clicking '{orders_btn.text}'...")
        await orders_btn.click()
        await asyncio.sleep(2.0)
        orders_msg = (await client.get_messages(BOT_USERNAME, limit=1))[0]
        print(f"\n--- ORDERS LIST MESSAGE ---")
        print(orders_msg.text or orders_msg.message)
        ces = [e for e in getattr(orders_msg, "entities", []) or [] if isinstance(e, MessageEntityCustomEmoji)]
        print(f"Orders Custom Emoji entities: {len(ces)}")

        # Click order detail if any order button exists
        order_detail_btn = None
        for row in orders_msg.buttons or []:
            for b in row:
                if "#" in b.text:
                    order_detail_btn = b
                    break
        
        if order_detail_btn:
            print(f"\nClicking order detail: '{order_detail_btn.text}'...")
            await order_detail_btn.click()
            await asyncio.sleep(2.0)
            detail_msg = (await client.get_messages(BOT_USERNAME, limit=1))[0]
            print(f"\n--- ORDER DETAIL MESSAGE ---")
            print(detail_msg.text or detail_msg.message)
            d_ces = [e for e in getattr(detail_msg, "entities", []) or [] if isinstance(e, MessageEntityCustomEmoji)]
            print(f"Order Detail Custom Emoji entities: {len(d_ces)}")
            for ce_ent in d_ces:
                print(f"  doc_id={ce_ent.document_id}")

if __name__ == "__main__":
    asyncio.run(main())
