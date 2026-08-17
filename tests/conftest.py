"""Shared pytest fixtures for isolated PostgreSQL database and API testing."""

import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.base import Base
from database.session import get_db_session, get_db_engine
from backend.config import settings
from backend.main import app


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    """Creates PostgreSQL engine using psycopg for reproducible test execution."""
    db_url = settings.DATABASE_URL
    engine = create_async_engine(db_url, echo=False)
    
    async def _init_tables():
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SEQUENCE IF NOT EXISTS incident_id_seq START 1"))
            await conn.run_sync(Base.metadata.create_all)

    async def _drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.execute(text("DROP SEQUENCE IF NOT EXISTS incident_id_seq"))
        await engine.dispose()

    try:
        asyncio.run(_init_tables())
    except Exception as e:
        pytest.skip(f"PostgreSQL server not available at {db_url}: {e}")

    yield engine

    try:
        asyncio.run(_drop_tables())
    except Exception:
        pass


@pytest.fixture()
def override_db_dependency(test_engine: AsyncEngine):
    """Overrides default get_db_session and get_db_engine FastAPI dependencies."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_db_engine] = lambda: test_engine
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_db_tables():
    """Truncates events and incidents tables between tests for test isolation."""
    try:
        db_url = settings.DATABASE_URL
        engine = create_async_engine(db_url, echo=False)
        async def _clean():
            async with engine.begin() as conn:
                await conn.execute(text("TRUNCATE TABLE events, incidents, detection_rules, detection_matches, incident_evidence, iocs, mitre_techniques, event_iocs, event_mitre_mappings, incident_notes, incident_audit_log RESTART IDENTITY CASCADE"))
            await engine.dispose()


        asyncio.run(_clean())
    except Exception:
        pass
    yield


