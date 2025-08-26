from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.infrastructure.config.settings import Settings, settings
from src.infrastructure.database.config import get_async_session


router = APIRouter(tags=["health"])


def get_settings() -> Settings:
    """Get application settings."""
    return settings


@router.get("/")
async def root(settings: Settings = Depends(get_settings)):
    """Welcome endpoint."""
    return {
        "message": f"Welcome to {settings.app.app_name}!",
        "version": settings.app.app_version,
        "architecture": "hexagonal",
        "dependency_injection": "Dishka 1.6"
    }


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings)
):
    """Health check endpoint with database connectivity test."""
    try:
        # Test database connection
        await session.execute(text("SELECT 1"))
        database_status = "healthy"
    except Exception as e:
        database_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if database_status == "healthy" else "degraded",
        "database": database_status,
        "architecture": "hexagonal",
        "dependency_injection": "Dishka 1.6",
        "app_name": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": "configured"
    }