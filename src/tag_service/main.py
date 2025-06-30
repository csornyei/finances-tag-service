import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from finances_shared.db import get_db, init_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tag_service.logger import logger
from tag_service.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(logger)
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_response(request: Request, call_next):
    """
    Middleware to log request and response details.
    """
    start_time = time.perf_counter()
    data = {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
    }
    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    data["process_time"] = process_time
    data["response"] = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
    }

    logger.info(data)

    return response


@app.middleware("http")
async def handle_exceptions(request: Request, call_next):
    """
    Middleware to handle exceptions and log them.
    """
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exception:
        logger.error(f"HTTP exception: {http_exception.detail}")
        return {"error": http_exception.detail}, http_exception.status_code
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return {"error": "Internal Server Error"}, 500


app.include_router(router, prefix="/api/v1", tags=["api"])


@app.get("/health", tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    """

    result = await db.execute(text("SELECT 1"))
    return {"status": "ok", "result": result.scalar_one()}
