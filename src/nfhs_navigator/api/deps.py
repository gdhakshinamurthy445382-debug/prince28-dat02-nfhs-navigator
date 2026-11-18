"""Shared FastAPI dependencies."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from nfhs_navigator.config import Settings, get_settings
from nfhs_navigator.indicator_store import IndicatorStore
from nfhs_navigator.store import RecordStore


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_store(request: Request) -> RecordStore:
    return request.app.state.store


@lru_cache
def get_indicator_store() -> IndicatorStore:
    settings = get_settings()
    store = IndicatorStore(settings.indicator_data_file)
    store.load()
    return store


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
StoreDep = Annotated[RecordStore, Depends(get_store)]
