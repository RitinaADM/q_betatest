import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
import uvicorn
from sqlalchemy.exc import SQLAlchemyError

# Import controllers
from src.infrastructure.adapters.inbound.rest.item_controller import router as item_router
from src.infrastructure.adapters.inbound.rest.health_controller import router as health_router
from src.infrastructure.adapters.inbound.rest.exception_handlers import EXCEPTION_HANDLERS
from src.infrastructure.database.config import create_tables
from src.infrastructure.config.settings import settings
from src.infrastructure.logging import logging_config, get_logger
from src.domain.exceptions import DomainException

# Setup logging
logging_config.setup_logging(use_json_format=False)
logger = get_logger(__name__, component="main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create database tables
    logger.info("Starting application startup", extra={"operation": "startup"})
    
    try:
        await create_tables()
        logger.info("Database tables created successfully", extra={"operation": "database_setup"})
    except Exception as e:
        logger.error("Failed to create database tables", exc_info=True, extra={"operation": "database_setup"})
        raise
    
    logger.info("Application startup completed", extra={"operation": "startup"})
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("Application shutdown initiated", extra={"operation": "shutdown"})
    logger.info("Application shutdown completed", extra={"operation": "shutdown"})


# Create FastAPI instance with hexagonal architecture
app = FastAPI(
    title=settings.app.app_name,
    description=settings.app.app_description,
    version=settings.app.app_version,
    lifespan=lifespan
)

# Register exception handlers
for exception_class, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_class, handler)

logger.info("Exception handlers registered", extra={"operation": "exception_handlers_setup"})

# Include routers
app.include_router(health_router)
app.include_router(item_router)

logger.info("Application routes configured", extra={"operation": "routes_setup"})


if __name__ == "__main__":
    logger.info(
        "Starting FastAPI server",
        extra={
            "operation": "server_start",
            "host": settings.server.host,
            "port": settings.server.port,
            "debug": settings.app.debug
        }
    )
    
    uvicorn.run(
        "main:app", 
        host=settings.server.host, 
        port=settings.server.port, 
        reload=settings.app.debug,  # Enable auto-reload in debug mode
        log_level=settings.server.log_level
    )
