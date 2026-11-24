import asyncio

from sqlalchemy import text

from nfhs_navigator.config import get_settings
from nfhs_navigator.db.session import make_engine


async def main():
    engine = make_engine(get_settings())
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT title FROM documents ORDER BY title"))
        for row in result:
            print(row.title)
    await engine.dispose()


asyncio.run(main())
