from typing import AsyncGenerator
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from ..config.settings import settings

# Database configuration from settings
DATABASE_URL = settings.database.database_url
SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.database.database_echo,
    future=True
)

# Create sync engine for migrations
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.database.database_echo,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

# Base class for ORM models
class Base(DeclarativeBase):
    """База данных для SQLAlchemy моделей."""
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.
    Used for dependency injection in FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """
    Dependency function to get sync database session.
    Used for migrations and initialization.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def create_tables():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def create_tables_sync():
    """Create all database tables synchronously."""
    Base.metadata.create_all(bind=sync_engine)


def drop_tables_sync():
    """Drop all database tables synchronously."""
    Base.metadata.drop_all(bind=sync_engine)