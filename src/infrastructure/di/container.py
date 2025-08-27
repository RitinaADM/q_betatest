"""
Контейнер для внедрения зависимостей (DI) на основе Dishka.
Организует регистрацию и предоставление всех зависимостей приложения.
"""

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
    """
    Провайдер для зависимостей, связанных с базой данных.
    Отвечает за создание и управление асинхронными сессиями SQLAlchemy.
    """
    
    # Область видимости провайдера
    scope = Scope.REQUEST
    
    @provide
    async def provide_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Предоставление асинхронной сессии базы данных.
        
        Автоматически управляет транзакциями:
        - Подтверждает транзакции при успешном завершении
        - Откатывает транзакции при ошибках
        - Гарантированно закрывает сессию
        
        Возвращает:
            Асинхронный генератор сессии базы данных
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


class RepositoryProvider(Provider):
    """
    Провайдер для реализаций репозиториев.
    Отвечает за создание конкретных реализаций репозиториев.
    """
    
    # Область видимости провайдера
    scope = Scope.REQUEST
    
    @provide
    def provide_item_repository(self, session: AsyncSession) -> ItemRepository:
        """
        Предоставление реализации репозитория элементов.
        
        Аргументы:
            session: Асинхронная сессия базы данных
            
        Возвращает:
            Реализация репозитория элементов на основе SQLAlchemy
        """
        return SQLAlchemyItemRepositoryAdapter(session)


class ServiceProvider(Provider):
    """
    Провайдер для сервисов приложения.
    Отвечает за создание сервисов и оркестрацию use case'ов.
    """
    
    # Область видимости провайдера
    scope = Scope.REQUEST
    
    @provide
    def provide_item_service_port(self, repository: ItemRepository) -> ItemServicePort:
        """
        Предоставление реализации порта сервиса элементов.
        
        Аргументы:
            repository: Репозиторий для работы с элементами
            
        Возвращает:
            Реализация сервиса элементов с использованием use case'ов
        """
        return ItemService(repository)


class ConfigProvider(Provider):
    """
    Провайдер для конфигурационных настроек.
    Отвечает за предоставление конфигурации приложения.
    """
    
    # Область видимости провайдера (все приложение)
    scope = Scope.APP
    
    @provide
    def provide_settings(self) -> Settings:
        """
        Предоставление настроек приложения.
        
        Возвращает:
            Объект настроек приложения с конфигурацией
        """
        return settings


def create_dishka_container() -> Container:
    """
    Создание и конфигурация контейнера Dishka DI.
    
    Объединяет все провайдеры в единый контейнер для внедрения зависимостей.
    Порядок регистрации провайдеров:
    1. Конфигурация приложения
    2. Компоненты базы данных
    3. Репозитории
    4. Сервисы приложения
    
    Возвращает:
        Настроенный контейнер внедрения зависимостей
    """
    return make_container(
        ConfigProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )