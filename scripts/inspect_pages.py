import asyncio
import sys

from sqlalchemy import text

from nfhs_navigator.config import get_settings
from nfhs_navigator.db.session import make_engine

SQL = """
SELECT d.title, p.page_no, p.headings, p.text
FROM documents d
JOIN pages p ON p.document_id = d.id
WHERE d.title ILIKE :title_pattern
  AND p.text ILIKE :page_pattern
ORDER BY p.page_no
LIMIT 6
"""


async def main(title: str, phrase: str) -> None:
    engine = make_engine(get_settings())
    async with engine.connect() as conn:
        result = await conn.execute(
            text(SQL),
            {"title_pattern": f"%{title}%", "page_pattern": f"%{phrase}%"},
        )
        rows = result.fetchall()
        if not rows:
            print("No matching pages found.")
        for row in rows:
            print("\n" + "=" * 90)
            print(f"DOCUMENT: {row.title}")
            print(f"PAGE: {row.page_no}")
            print(f"HEADINGS: {row.headings}")
            print("-" * 90)
            print((row.text or "")[:3500])
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: uv run python scripts/inspect_pages.py <title-word> <page-search-phrase>")
    asyncio.run(main(sys.argv[1], sys.argv[2]))
