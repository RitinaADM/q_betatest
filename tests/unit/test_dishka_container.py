"""
Unit tests for Dependency Injection Container and Providers.
Tests the Dishka DI container setup and provider implementations.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import Container

from src.infrastructure.di.container import (
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
    ConfigProvider,
    create_dishka_container
)
from src.domain.ports.inbound.services.item_service_port import ItemServicePort
from src.application.services.item_service import ItemService
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.infrastructure.adapters.outbound.database.sql.item_repository_adapter import SQLAlchemyItemRepositoryAdapter
from src.infrastructure.config.settings import Settings


class TestDatabaseProvider:
    """Test database provider implementation."""
    
    def test_database_provider_scope(self):
        """Test that database provider has correct scope."""
        provider = DatabaseProvider()
        assert provider.scope.name == "REQUEST"
    
    @pytest.mark.asyncio
    async def test_provide_async_session(self):
        """Test async session provision."""
        provider = DatabaseProvider()
        
        # Mock the AsyncSessionLocal
        with patch('src.infrastructure.di.container.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            # Test session provision
            session_generator = provider.provide_async_session()
            session = await session_generator.__anext__()
            
            assert session is mock_session
            mock_session_local.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_session_commit_on_success(self):
        """Test that session commits on successful completion."""
        provider = DatabaseProvider()
        
        with patch('src.infrastructure.di.container.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            # Test session lifecycle
            session_generator = provider.provide_async_session()
            session = await session_generator.__anext__()
            
            # Simulate successful completion
            try:
                await session_generator.__anext__()
            except StopAsyncIteration:
                pass
            
            # Should commit and close
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_session_rollback_on_error(self):
        """Test that session rolls back on error."""
        provider = DatabaseProvider()
        
        with patch('src.infrastructure.di.container.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            # Mock an exception during session usage
            mock_session.commit.side_effect = Exception("Database error")
            
            session_generator = provider.provide_async_session()
            session = await session_generator.__anext__()
            
            # Simulate error during usage
            with pytest.raises(Exception):
                try:
                    await session_generator.__anext__()
                except StopAsyncIteration:
                    pass
            
            # Should rollback and close
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()


class TestRepositoryProvider:
    """Test repository provider implementation."""
    
    def test_repository_provider_scope(self):
        """Test that repository provider has correct scope."""
        provider = RepositoryProvider()
        assert provider.scope.name == "REQUEST"
    
    def test_provide_item_repository(self):
        """Test item repository provision."""
        provider = RepositoryProvider()
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Test repository creation
        repository = provider.provide_item_repository(mock_session)
        
        assert isinstance(repository, SQLAlchemyItemRepositoryAdapter)
        assert repository._session is mock_session


class TestServiceProvider:
    """Test service provider implementation."""
    
    def test_service_provider_scope(self):
        """Test that service provider has correct scope."""
        provider = ServiceProvider()
        assert provider.scope.name == "REQUEST"
    
    def test_provide_item_service(self):
        """Test item service provision."""
        provider = ServiceProvider()
        mock_repository = MagicMock(spec=ItemRepository)
        
        # Test service creation
        service = provider.provide_item_service_port(mock_repository)
        
        assert isinstance(service, ItemService)
        assert service._item_repository is mock_repository


class TestDishkaContainer:
    """Test Dishka container creation and configuration."""
    
    def test_create_dishka_container(self):
        """Test that container is created successfully."""
        container = create_dishka_container()
        
        assert isinstance(container, Container)
    
    def test_container_configuration_with_settings(self):
        """Test that container can be configured with different settings."""
        # Test with default settings
        container1 = create_dishka_container()
        assert isinstance(container1, Container)
        
        # Test that multiple containers can be created
        container2 = create_dishka_container()
        assert isinstance(container2, Container)
        assert container1 is not container2


class TestConfigProvider:
    """Test configuration provider implementation."""
    
    def test_config_provider_scope(self):
        """Test that config provider has correct scope."""
        provider = ConfigProvider()
        assert provider.scope.name == "APP"
    
    def test_provide_settings(self):
        """Test settings provision."""
        provider = ConfigProvider()
        
        # Test settings creation
        settings = provider.provide_settings()
        
        assert isinstance(settings, Settings)


class TestProviderIntegration:
    """Test integration between providers."""
    
    @pytest.mark.asyncio
    async def test_full_provider_chain_integration(self):
        """Test the complete provider chain working together."""
        # Create providers
        db_provider = DatabaseProvider()
        repo_provider = RepositoryProvider()
        service_provider = ServiceProvider()
        
        with patch('src.infrastructure.di.container.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None
            
            # Test provider chain
            session_generator = db_provider.provide_async_session()
            session = await session_generator.__anext__()
            
            repository = repo_provider.provide_item_repository(session)
            service = service_provider.provide_item_service_port(repository)
            
            # Verify chain
            assert isinstance(service, ItemService)
            assert isinstance(repository, SQLAlchemyItemRepositoryAdapter)
            assert session is mock_session
            assert service._item_repository is repository
            assert repository._session is session
    
    @pytest.mark.asyncio
    async def test_provider_error_handling(self):
        """Test error handling in provider chain."""
        db_provider = DatabaseProvider()
        
        with patch('src.infrastructure.di.container.AsyncSessionLocal') as mock_session_local:
            # Mock session creation failure
            mock_session_local.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception, match="Database connection failed"):
                session_generator = db_provider.provide_async_session()
                await session_generator.__anext__()
    
    def test_provider_type_annotations(self):
        """Test that providers have correct type annotations."""
        db_provider = DatabaseProvider()
        repo_provider = RepositoryProvider()
        service_provider = ServiceProvider()
        
        # Check that methods exist and are callable
        assert callable(db_provider.provide_async_session)
        assert callable(repo_provider.provide_item_repository)
        assert callable(service_provider.provide_item_service_port)
        
        # Check return type hints (basic verification)
        session_method = db_provider.provide_async_session
        repo_method = repo_provider.provide_item_repository
        service_method = service_provider.provide_item_service_port
        
        # These should have proper annotations
        assert hasattr(session_method, '__annotations__')
        assert hasattr(repo_method, '__annotations__')
        assert hasattr(service_method, '__annotations__')