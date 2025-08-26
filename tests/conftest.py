"""
Test configuration and fixtures.
Provides shared fixtures for unit and integration tests.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine

from src.infrastructure.database.config import Base
from src.infrastructure.database.models import ItemModel


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide async database session for testing.
    Each test gets a fresh session with rollback after test completion.
    """
    # Create test engine directly
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
    
    # Clean up engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_session: AsyncSession) -> AsyncSession:
    """
    Alias for async_session to maintain compatibility.
    """
    return async_session


# SQLite specific configuration for testing
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(async_session: AsyncSession):
    """
    Clean database before each test.
    This fixture runs automatically before each test.
    """
    # Clean up all tables in reverse order (to handle foreign keys)
    try:
        await async_session.execute(ItemModel.__table__.delete())
        await async_session.commit()
    except Exception:
        await async_session.rollback()
