"""Dependencies: endpoints ask for these instead of building them."""

import asyncio
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from nfhs_navigator.config import Settings
from nfhs_navigator.db.repository import DocumentRepository
from nfhs_navigator.indicator_store import IndicatorStore


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_indicator_store(request: Request) -> IndicatorStore:
    """Return the application-wide indicator store."""
    return request.app.state.indicator_store


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """One session per request, closed automatically afterwards."""
    async with request.app.state.sessionmaker() as session:
        yield session


async def get_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> DocumentRepository:
    return DocumentRepository(session)


async def check_db(request: Request) -> bool:
    """Can we run SELECT 1 within 2 seconds?"""
    try:
        async with request.app.state.engine.connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=2)
        return True
    except Exception:
        return False


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
RepoDep = Annotated[DocumentRepository, Depends(get_repo)]
DbCheckDep = Annotated[bool, Depends(check_db)]
