import asyncio
from sqlalchemy import select, delete
from bot.database.engine import session_factory
from bot.database.models import Category, Product

async def main():
    async with session_factory() as session:
        # Check categories
        cats = list((await session.execute(select(Category))).scalars().all())
        seen_cats = {}
        for c in cats:
            clean = c.name.lstrip("⚡️💎🧠🤖🔑💻🌐🛡🎮🕹 ").strip()
            if clean in seen_cats:
                # Merge products to seen_cats[clean]
                prods = list((await session.execute(select(Product).where(Product.category_id == c.id))).scalars().all())
                for p in prods:
                    p.category_id = seen_cats[clean].id
                await session.delete(c)
            else:
                c.name = clean
                seen_cats[clean] = c
        await session.commit()

        # Check products
        prods = list((await session.execute(select(Product))).scalars().all())
        seen_prods = {}
        for p in prods:
            clean = p.name.lstrip("⭐️⭐🔮🎧🎬🧠🎨⚡️🪟📊🛡🔒🎮🕹 ").replace("—", "•").strip()
            key = (clean, p.category_id)
            if key in seen_prods:
                await session.delete(p)
            else:
                p.name = clean
                seen_prods[key] = p
        await session.commit()
        print("Deduplication completed!")

if __name__ == "__main__":
    asyncio.run(main())
