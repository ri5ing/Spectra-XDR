"""Database Engine and Session Factory configuration."""

import sys
import asyncio
from typing import AsyncGenerator, Dict, Any

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("spectra.database.session")


def create_engine_instance(url: str = settings.DATABASE_URL) -> AsyncEngine:
    """Creates a configured AsyncEngine instance."""
    kwargs: Dict[str, Any] = {
        "echo": settings.DATABASE_ECHO,
    }
    if "postgresql" in url or "postgres" in url:
        kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
        kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        
    return create_async_engine(url, **kwargs)


engine: AsyncEngine = create_engine_instance()

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


def get_db_engine() -> AsyncEngine:
    """Returns the application AsyncEngine instance."""
    return engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health(db_engine: AsyncEngine = engine) -> Dict[str, Any]:
    """Performs a read-only database ping query."""
    try:
        async with db_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            return {
                "status": "healthy",
                "service": "postgresql"
            }
    except Exception as e:
        logger.warning(f"Database health check ping failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "postgresql",
            "error": str(e)
        }

