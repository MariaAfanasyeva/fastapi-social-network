import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from social_network.database import database
from social_network.logging_conf import configure_logging
from social_network.routers.post import router as post_router
from social_network.routers.upload import router as upload_router
from social_network.routers.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


app.include_router(post_router)
app.include_router(user_router)
app.include_router(upload_router)


@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exception):
    logger.error(f"HTTPexception: {exception.status_code} {exception.detail}")
    return await http_exception_handler(request, exception)
