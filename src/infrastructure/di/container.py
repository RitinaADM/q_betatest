from typing import AsyncGenerator
from dishka import Container, make_container, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.ports.inbound.services.item_service_port import ItemServicePort
from src.application.services.item_service import ItemService
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.infrastructure.adapters.outbound.database.sql.item_repository_adapter import SQLAlchemyItemRepositoryAdapter
from src.infrastructure.database.config import AsyncSessionLocal
from src.infrastructure.config.settings import Settings, settings


class DatabaseProvider(Provider):
    """Provider for database-related dependencies."""
    
    scope = Scope.REQUEST
    
    @provide
    async def provide_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide async database session."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class RepositoryProvider(Provider):
    """Provider for repository implementations."""
    
    scope = Scope.REQUEST
    
    @provide
    def provide_item_repository(self, session: AsyncSession) -> ItemRepository:
        """Provide item repository implementation."""
        return SQLAlchemyItemRepositoryAdapter(session)


class ServiceProvider(Provider):
    """Provider for application services."""
    
    scope = Scope.REQUEST
    
    @provide
    def provide_item_service_port(self, repository: ItemRepository) -> ItemServicePort:
        """Provide item service port implementation."""
        return ItemService(repository)


class ConfigProvider(Provider):
    """Provider for configuration settings."""
    
    scope = Scope.APP
    
    @provide
    def provide_settings(self) -> Settings:
        """Provide application settings."""
        return settings


def create_dishka_container() -> Container:
    """Create and configure Dishka DI container."""
    return make_container(
        ConfigProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )