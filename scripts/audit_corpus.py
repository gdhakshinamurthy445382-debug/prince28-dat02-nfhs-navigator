import asyncio
import json
from pathlib import Path

from sqlalchemy import text

from nfhs_navigator.config import get_settings
from nfhs_navigator.db.session import make_engine


async def main():
    manifest = Path("data/manifest.jsonl")
    files = [
        json.loads(line)
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    engine = make_engine(get_settings())
    async with engine.connect() as conn:
        documents = await conn.scalar(text("SELECT COUNT(*) FROM documents"))
        parsed = await conn.scalar(text("SELECT COUNT(DISTINCT document_id) FROM pages"))
        pages = await conn.scalar(text("SELECT COUNT(*) FROM pages"))
        failures = await conn.scalar(text("SELECT COUNT(*) FROM parse_failures"))
        reasons = await conn.execute(
            text("SELECT reason, COUNT(*) FROM parse_failures GROUP BY reason ORDER BY reason")
        )

    await engine.dispose()

    print(f"Manifest files: {len(files)}")
    print(f"Documents in database: {documents}")
    print(f"Parsed documents: {parsed}")
    print(f"Failed files: {failures}")
    print(f"Pages in PostgreSQL: {pages}")
    print(f"Parsing coverage: {parsed / len(files) * 100:.1f}%")
    print("\nFailures by reason:")
    for reason, count in reasons:
        print(f"{reason}: {count}")


if __name__ == "__main__":
    asyncio.run(main())
