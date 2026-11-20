"""App factory: build a fully wired FastAPI app from settings."""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from nfhs_navigator.api.errors import register_error_handlers
from nfhs_navigator.api.middleware import request_context
from nfhs_navigator.api.routes import documents, health, indicators
from nfhs_navigator.config import Settings, get_settings
from nfhs_navigator.db.session import make_engine, make_sessionmaker
from nfhs_navigator.indicator_store import IndicatorStore
from nfhs_navigator.logging_setup import setup_logging

logger = logging.getLogger("nfhs_navigator")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    setup_logging(settings.log_level)
    engine = make_engine(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("starting", extra={"status": settings.app_env})
        yield
        await engine.dispose()

    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)

    indicator_store = IndicatorStore(settings.indicator_data_file)
    indicator_store.load()
    app.state.indicator_store = indicator_store

    app.middleware("http")(request_context)
    register_error_handlers(app)

    v1 = APIRouter(prefix="/v1")
    v1.include_router(documents.router)
    v1.include_router(indicators.router)

    app.include_router(health.router)
    app.include_router(v1)
    return app
