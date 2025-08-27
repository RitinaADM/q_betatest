"""
Unit tests for Item Repository implementations.
Tests the SQLAlchemy repository implementation with mocked database operations.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.domain.entities.item import Item
from src.domain.exceptions import DuplicateItemError
from src.infrastructure.adapters.outbound.database.sql.item_repository_adapter import SQLAlchemyItemRepositoryAdapter
from src.infrastructure.database.models import ItemModel


class TestSQLAlchemyItemRepositoryAdapter:
    """Test SQLAlchemy item repository adapter implementation."""

    @pytest.fixture
    def mock_session(self):
        """Provide mocked AsyncSession."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Provide repository adapter instance with mocked session."""
        return SQLAlchemyItemRepositoryAdapter(mock_session)

    @pytest.fixture
    def sample_item(self):
        """Provide sample item entity."""
        return Item(
            id=1,
            name="Test Item",
            description="A test item",
            price=Decimal("29.99"),
            in_stock=True
        )

    @pytest.fixture
    def sample_item_model(self, sample_item):
        """Provide sample item database model."""
        model = ItemModel(
            id=sample_item.id,
            name=sample_item.name,
            description=sample_item.description,
            price=float(sample_item.price),
            in_stock=sample_item.in_stock
        )
        return model

    @pytest.mark.asyncio
    async def test_create_item_success(self, repository, mock_session, sample_item):
        """Test successful item creation."""
        # Arrange
        new_item = Item(
            id=None,
            name="New Item",
            description="A new test item",
            price=Decimal("49.99"),
            in_stock=True
        )
        
        created_model = ItemModel(
            id=1,
            name=new_item.name,
            description=new_item.description,
            price=float(new_item.price),
            in_stock=new_item.in_stock
        )
        
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock exists_by_name to return False (no duplicate)
        with patch.object(repository, 'exists_by_name', return_value=False) as mock_exists:
            # Mock the model creation and conversion
            with patch.object(ItemModel, 'from_domain_entity', return_value=created_model) as mock_from_domain:
                with patch.object(created_model, 'to_domain_entity') as mock_to_domain:
                    expected_item = Item(
                        id=1,
                        name=new_item.name,
                        description=new_item.description,
                        price=new_item.price,
                        in_stock=new_item.in_stock
                    )
                    mock_to_domain.return_value = expected_item
                    
                    # Act
                    result = await repository.create(new_item)
                    
                    # Assert
                    mock_exists.assert_called_once_with(new_item.name)
                    mock_from_domain.assert_called_once_with(new_item)
                    mock_session.add.assert_called_once_with(created_model)
                    mock_session.flush.assert_called_once()
                    mock_session.refresh.assert_called_once_with(created_model)
                    mock_to_domain.assert_called_once()
                    assert result == expected_item

    @pytest.mark.asyncio
    async def test_create_item_duplicate_error(self, repository, mock_session):
        """Test item creation fails with duplicate name."""
        # Arrange
        duplicate_item = Item(
            id=None,
            name="Duplicate Item",
            description="A duplicate item",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Mock exists_by_name to return True (duplicate found)
        with patch.object(repository, 'exists_by_name', return_value=True) as mock_exists:
            # Act & Assert
            with pytest.raises(DuplicateItemError) as exc_info:
                await repository.create(duplicate_item)
            
            assert duplicate_item.name in str(exc_info.value)
            mock_exists.assert_called_once_with(duplicate_item.name)
            # Session methods should not be called since we detect duplicate early
            mock_session.add.assert_not_called()
            mock_session.flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_item, sample_item_model):
        """Test getting item by ID when item exists."""
        # Arrange
        item_id = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_item_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with patch.object(sample_item_model, 'to_domain_entity', return_value=sample_item):
            # Act
            result = await repository.get_by_id(item_id)
            
            # Assert
            mock_session.execute.assert_called_once()
            assert result == sample_item

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting item by ID when item doesn't exist."""
        # Arrange
        item_id = 999
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get_by_id(item_id)
        
        # Assert
        mock_session.execute.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_items(self, repository, mock_session):
        """Test getting all items."""
        # Arrange
        item_models = [
            ItemModel(id=1, name="Item 1", description="Desc 1", price=10.0, in_stock=True),
            ItemModel(id=2, name="Item 2", description="Desc 2", price=20.0, in_stock=False),
            ItemModel(id=3, name="Item 3", description="Desc 3", price=30.0, in_stock=True),
        ]
        
        expected_items = [
            Item(id=1, name="Item 1", description="Desc 1", price=Decimal("10.0"), in_stock=True),
            Item(id=2, name="Item 2", description="Desc 2", price=Decimal("20.0"), in_stock=False),
            Item(id=3, name="Item 3", description="Desc 3", price=Decimal("30.0"), in_stock=True),
        ]
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = item_models
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock to_domain_entity for each model
        for i, (model, expected) in enumerate(zip(item_models, expected_items)):
            with patch.object(model, 'to_domain_entity', return_value=expected):
                pass
        
        # Patch all models to return expected items
        with patch.object(ItemModel, 'to_domain_entity') as mock_to_domain:
            mock_to_domain.side_effect = expected_items
            
            # Act
            result = await repository.get_all()
            
            # Assert
            mock_session.execute.assert_called_once()
            assert len(result) == 3
            assert all(isinstance(item, Item) for item in result)

    @pytest.mark.asyncio
    async def test_update_item_success(self, repository, mock_session, sample_item):
        """Test successful item update."""
        # Arrange
        updated_item = Item(
            id=1,
            name="Updated Item",
            description="Updated description",
            price=Decimal("39.99"),
            in_stock=False
        )
        
        existing_model = ItemModel(
            id=1,
            name="Old Item",
            description="Old description",
            price=29.99,
            in_stock=True
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        existing_model.update_from_domain_entity = MagicMock()
        
        with patch.object(existing_model, 'to_domain_entity', return_value=updated_item):
            # Act
            result = await repository.update(updated_item)
            
            # Assert
            mock_session.execute.assert_called_once()
            existing_model.update_from_domain_entity.assert_called_once_with(updated_item)
            mock_session.flush.assert_called_once()
            mock_session.refresh.assert_called_once_with(existing_model)
            assert result == updated_item

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, repository, mock_session):
        """Test updating non-existent item."""
        # Arrange
        non_existent_item = Item(
            id=999,
            name="Non-existent Item",
            description="Does not exist",
            price=Decimal("99.99"),
            in_stock=True
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.update(non_existent_item)
        
        # Assert
        mock_session.execute.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_item_success(self, repository, mock_session):
        """Test successful item deletion."""
        # Arrange
        item_id = 1
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.delete(item_id)
        
        # Assert
        mock_session.execute.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, repository, mock_session):
        """Test deleting non-existent item."""
        # Arrange
        item_id = 999
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.delete(item_id)
        
        # Assert
        mock_session.execute.assert_called_once()
        assert result is False

    @pytest.mark.asyncio
    async def test_search_by_name(self, repository, mock_session):
        """Test searching items by name."""
        # Arrange
        search_query = "laptop"
        matching_models = [
            ItemModel(id=1, name="Gaming Laptop", description="High-end laptop", price=1299.99, in_stock=True),
            ItemModel(id=2, name="Office Laptop", description="Business laptop", price=899.99, in_stock=True),
        ]
        
        expected_items = [
            Item(id=1, name="Gaming Laptop", description="High-end laptop", price=Decimal("1299.99"), in_stock=True),
            Item(id=2, name="Office Laptop", description="Business laptop", price=Decimal("899.99"), in_stock=True),
        ]
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = matching_models
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock to_domain_entity for each model
        with patch.object(ItemModel, 'to_domain_entity') as mock_to_domain:
            mock_to_domain.side_effect = expected_items
            
            # Act
            result = await repository.search_by_name(search_query)
            
            # Assert
            mock_session.execute.assert_called_once()
            assert len(result) == 2
            assert all("laptop" in item.name.lower() for item in result)

    @pytest.mark.asyncio
    async def test_search_by_name_no_results(self, repository, mock_session):
        """Test searching with no matching results."""
        # Arrange
        search_query = "nonexistent"
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.search_by_name(search_query)
        
        # Assert
        mock_session.execute.assert_called_once()
        assert result == []

    @pytest.mark.asyncio
    async def test_search_by_description(self, repository, mock_session):
        """Test searching items by description content."""
        # Arrange
        search_query = "gaming"
        matching_models = [
            ItemModel(id=1, name="Laptop", description="Gaming laptop with RTX", price=1299.99, in_stock=True),
            ItemModel(id=2, name="Mouse", description="Gaming mouse with RGB", price=59.99, in_stock=True),
        ]
        
        expected_items = [
            Item(id=1, name="Laptop", description="Gaming laptop with RTX", price=Decimal("1299.99"), in_stock=True),
            Item(id=2, name="Mouse", description="Gaming mouse with RGB", price=Decimal("59.99"), in_stock=True),
        ]
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = matching_models
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock to_domain_entity for each model
        with patch.object(ItemModel, 'to_domain_entity') as mock_to_domain:
            mock_to_domain.side_effect = expected_items
            
            # Act
            result = await repository.search_by_name(search_query)
            
            # Assert
            mock_session.execute.assert_called_once()
            assert len(result) == 2
            assert all("gaming" in item.description.lower() for item in result)

    @pytest.mark.asyncio 
    async def test_repository_session_management(self, mock_session):
        """Test that repository properly uses the provided session."""
        # Arrange
        repository = SQLAlchemyItemRepositoryAdapter(mock_session)
        
        # Act & Assert
        assert repository._session is mock_session
        
        # Test that session is used in operations
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        await repository.get_by_id(1)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_item_with_none_id(self, repository, mock_session):
        """Test creating item with None ID (auto-increment scenario)."""
        # Arrange
        new_item = Item(
            id=None,
            name="Auto ID Item",
            description="Item with auto-generated ID",
            price=Decimal("25.99"),
            in_stock=True
        )
        
        created_model = ItemModel(
            id=5,  # Auto-generated ID
            name=new_item.name,
            description=new_item.description,
            price=float(new_item.price),
            in_stock=new_item.in_stock
        )
        
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock exists_by_name to return False (no duplicate)
        with patch.object(repository, 'exists_by_name', return_value=False) as mock_exists:
            with patch.object(ItemModel, 'from_domain_entity', return_value=created_model):
                with patch.object(created_model, 'to_domain_entity') as mock_to_domain:
                    expected_item = Item(
                        id=5,
                        name=new_item.name,
                        description=new_item.description,
                        price=new_item.price,
                        in_stock=new_item.in_stock
                    )
                    mock_to_domain.return_value = expected_item
                    
                    # Act
                    result = await repository.create(new_item)
                    
                    # Assert
                    mock_exists.assert_called_once_with(new_item.name)
                    assert result.id == 5
                    assert result.name == new_item.name
                    mock_session.add.assert_called_once()
                    mock_session.flush.assert_called_once()
                    mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_error_handling(self, repository, mock_session):
        """Test repository handles database errors properly."""
        # Arrange
        item_id = 1
        mock_session.execute = AsyncMock(side_effect=Exception("Database connection lost"))
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection lost"):
            await repository.get_by_id(item_id)