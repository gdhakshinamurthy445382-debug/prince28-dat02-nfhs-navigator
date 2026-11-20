import os
import subprocess
import sys
import uuid
from urllib.parse import urlsplit, urlunsplit

import pytest
from sqlalchemy import text

from nfhs_navigator.config import Settings
from nfhs_navigator.db.models import Document
from nfhs_navigator.db.session import make_engine, make_sessionmaker

ROWS = [
    {"id": "001", "title": "Alpha", "kind": "circular", "year": 2024, "tags": ["a", "b"]},
    {"id": "002", "title": "Beta", "kind": "guideline", "year": 2025, "tags": ["b"]},
    {"id": "003", "title": "Gamma", "kind": "circular", "year": 2025, "tags": []},
]


@pytest.fixture(scope="session")
def database_url():
    """Create a fresh PostgreSQL database, migrate it, then drop it after the run."""
    import asyncio

    import asyncpg

    base_url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://app:app@localhost:5433/app_test",  # pragma: allowlist secret
    )

    parsed = urlsplit(base_url)
    database_name = f"nfhs_test_{uuid.uuid4().hex[:12]}"

    admin_url = urlunsplit(
        (parsed.scheme, parsed.netloc, "/postgres", parsed.query, parsed.fragment)
    )
    test_url = urlunsplit(
        (parsed.scheme, parsed.netloc, f"/{database_name}", parsed.query, parsed.fragment)
    )

    async def create_database():
        conn = await asyncpg.connect(admin_url)
        try:
            await conn.execute(f'CREATE DATABASE "{database_name}"')
        finally:
            await conn.close()

    async def drop_database():
        conn = await asyncpg.connect(admin_url)
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
        finally:
            await conn.close()

    asyncio.run(create_database())

    try:
        env = {
            **os.environ,
            "APP_ENV": "ci",
            "DATABASE_URL": test_url,
        }

        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env=env,
            check=True,
        )

        yield test_url
    finally:
        asyncio.run(drop_database())


@pytest.fixture
def settings(database_url):
    return Settings(app_env="ci", database_url=database_url, _env_file=None)


@pytest.fixture
async def seeded(settings):
    """Fresh rows for each test: delete, insert, and hand back the settings."""
    engine = make_engine(settings)

    async with make_sessionmaker(engine)() as session, session.begin():
        await session.execute(text("DELETE FROM documents"))

        for r in ROWS:
            meta = {k: v for k, v in r.items() if k not in ("id", "title")}
            session.add(
                Document(
                    external_id=r["id"],
                    title=r["title"],
                    sha256=r["id"] * 21,
                    metadata_=meta,
                )
            )

    await engine.dispose()
    return settings
