import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(r"C:\Users\dev\.gemini\antigravity\scratch\tg_assistant\.env")
from telethon import TelegramClient
from telethon.tl.functions.messages import GetCustomEmojiDocumentsRequest, GetStickerSetRequest
from telethon.tl.types import InputStickerSetID, DocumentAttributeSticker

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

sys.stdout.reconfigure(encoding="utf-8")

async def main():
    session_path = r"C:\Users\dev\.gemini\antigravity\scratch\tg_assistant\my_userbot"
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    docs = await client(GetCustomEmojiDocumentsRequest(document_id=[5258134813302332906]))
    for d in docs:
        for attr in getattr(d, 'attributes', []):
            if isinstance(attr, DocumentAttributeSticker):
                stickerset = attr.stickerset
                print(f"StickerSet ref: {stickerset}")
                full_set = await client(GetStickerSetRequest(stickerset=stickerset, hash=0))
                print(f"Set title: '{full_set.set.title}', short_name: '{full_set.set.short_name}', count: {len(full_set.documents)}")
                for doc in full_set.documents:
                    alts = [getattr(a, 'alt', '') for a in doc.attributes if hasattr(a, 'alt')]
                    print(f"  {doc.id}: {alts}")

if __name__ == "__main__":
    asyncio.run(main())
