from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextlib import AbstractAsyncContextManager
from collections.abc import Callable

from fastapi import FastAPI

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_lifespan() -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configuration = getattr(app.state, "api_configuration", None)
        if configuration is not None:
            logger.info(
                "API setup done, server listening on %s:%d",
                configuration.host,
                configuration.port,
            )
        else:
            logger.info("API setup done, server listening")
        app.state.is_ready = True
        yield
        app.state.is_ready = False
        logger.info("API server shutdown completed")

    return lifespan
