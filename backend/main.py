"""Main FastAPI Application Entrypoint for SPECTRA-XDR."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.router import api_router
from backend.config import settings
from backend.logging_config import setup_logging, get_logger

# Initialize logger
setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
logger = get_logger("spectra.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle context manager."""
    logger.info(f"Starting {settings.APP_NAME} in environment: {settings.APP_ENV}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Hybrid Multi-Agent XDR Architecture Foundation",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Register API Router
app.include_router(api_router)


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles HTTP exceptions with consistent JSON format."""
    logger.warning(f"HTTP exception on {request.method} {request.url.path}: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )



@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handles unhandled exceptions without leaking stack traces in production."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    
    detail = str(exc) if settings.DEBUG else "An internal server error occurred."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "status_code": 500,
            "detail": detail
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
