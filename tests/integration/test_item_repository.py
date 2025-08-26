"""
Integration tests for Item Repository implementations.
Tests the SQLAlchemy repository implementation with real database operations.
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.item import Item
from src.domain.exceptions import DuplicateItemError
from src.infrastructure.adapters.outbound.database.sql.item_repository_adapter import SQLAlchemyItemRepositoryAdapter


@pytest.mark.integration
class TestSQLAlchemyItemRepositoryAdapterIntegration:
    """Integration tests for SQLAlchemy item repository adapter with real database."""

    @pytest_asyncio.fixture
    async def repository(self, async_session: AsyncSession):
        """Provide repository adapter instance with real database session."""
        return SQLAlchemyItemRepositoryAdapter(async_session)

    @pytest.fixture
    def sample_items(self):
        """Provide sample items for testing."""
        return [
            Item(
                id=None,
                name="Integration Test Item 1",
                description="First test item for integration testing",
                price=Decimal("29.99"),
                in_stock=True
            ),
            Item(
                id=None,
                name="Integration Test Item 2", 
                description="Second test item for integration testing",
                price=Decimal("49.99"),
                in_stock=False
            ),
            Item(
                id=None,
                name="Gaming Laptop Integration",
                description="High-performance gaming laptop for integration tests",
                price=Decimal("1299.99"),
                in_stock=True
            )
        ]

    @pytest.mark.asyncio
    async def test_create_and_retrieve_item(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test creating an item and retrieving it by ID."""
        # Arrange
        new_item = Item(
            id=None,
            name="Test Creation Item",
            description="Item created for testing create and retrieve",
            price=Decimal("35.99"),
            in_stock=True
        )
        
        # Act - Create item
        created_item = await repository.create(new_item)
        
        # Assert creation
        assert created_item.id is not None
        assert created_item.name == new_item.name
        assert created_item.description == new_item.description
        assert created_item.price == new_item.price
        assert created_item.in_stock == new_item.in_stock
        
        # Act - Retrieve item
        retrieved_item = await repository.get_by_id(created_item.id)
        
        # Assert retrieval
        assert retrieved_item is not None
        assert retrieved_item.id == created_item.id
        assert retrieved_item.name == created_item.name
        assert retrieved_item.description == created_item.description
        assert retrieved_item.price == created_item.price
        assert retrieved_item.in_stock == created_item.in_stock

    @pytest.mark.asyncio
    async def test_create_multiple_items_and_get_all(self, repository: SQLAlchemyItemRepositoryAdapter, sample_items: List[Item]):
        """Test creating multiple items and retrieving all."""
        # Act - Create multiple items
        created_items = []
        for item in sample_items:
            created_item = await repository.create(item)
            created_items.append(created_item)
        
        # Assert creation
        assert len(created_items) == len(sample_items)
        for created_item in created_items:
            assert created_item.id is not None
        
        # Act - Get all items
        all_items = await repository.get_all()
        
        # Assert retrieval
        assert len(all_items) >= len(created_items)
        
        # Check that our created items are in the results
        created_ids = {item.id for item in created_items}
        retrieved_ids = {item.id for item in all_items}
        assert created_ids.issubset(retrieved_ids)

    @pytest.mark.asyncio
    async def test_update_item(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test updating an existing item."""
        # Arrange - Create initial item
        original_item = Item(
            id=None,
            name="Original Item",
            description="Original description",
            price=Decimal("25.00"),
            in_stock=True
        )
        
        created_item = await repository.create(original_item)
        
        # Act - Update item
        updated_item = Item(
            id=created_item.id,
            name="Updated Item Name",
            description="Updated description with more details",
            price=Decimal("35.00"),
            in_stock=False
        )
        
        result = await repository.update(updated_item)
        
        # Assert update
        assert result is not None
        assert result.id == created_item.id
        assert result.name == updated_item.name
        assert result.description == updated_item.description
        assert result.price == updated_item.price
        assert result.in_stock == updated_item.in_stock
        
        # Verify persistence by retrieving again
        retrieved_item = await repository.get_by_id(created_item.id)
        assert retrieved_item.name == updated_item.name
        assert retrieved_item.description == updated_item.description
        assert retrieved_item.price == updated_item.price
        assert retrieved_item.in_stock == updated_item.in_stock

    @pytest.mark.asyncio
    async def test_update_nonexistent_item(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test updating an item that doesn't exist."""
        # Arrange
        nonexistent_item = Item(
            id=99999,  # Very unlikely to exist
            name="Nonexistent Item",
            description="This item does not exist",
            price=Decimal("100.00"),
            in_stock=True
        )
        
        # Act
        result = await repository.update(nonexistent_item)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_item(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test deleting an existing item."""
        # Arrange - Create item to delete
        item_to_delete = Item(
            id=None,
            name="Item to Delete",
            description="This item will be deleted",
            price=Decimal("15.99"),
            in_stock=True
        )
        
        created_item = await repository.create(item_to_delete)
        created_id = created_item.id
        
        # Verify item exists
        retrieved_before = await repository.get_by_id(created_id)
        assert retrieved_before is not None
        
        # Act - Delete item
        deletion_result = await repository.delete(created_id)
        
        # Assert deletion
        assert deletion_result is True
        
        # Verify item no longer exists
        retrieved_after = await repository.get_by_id(created_id)
        assert retrieved_after is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_item(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test deleting an item that doesn't exist."""
        # Act
        result = await repository.delete(99999)  # Very unlikely to exist
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_search_by_name(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test searching items by name."""
        # Arrange - Create items with searchable names
        search_items = [
            Item(id=None, name="Gaming Laptop Pro", description="High-end gaming", price=Decimal("1299.99"), in_stock=True),
            Item(id=None, name="Office Laptop Basic", description="Basic office work", price=Decimal("599.99"), in_stock=True),
            Item(id=None, name="Gaming Mouse RGB", description="RGB gaming mouse", price=Decimal("79.99"), in_stock=False),
            Item(id=None, name="Wireless Keyboard", description="Standard keyboard", price=Decimal("39.99"), in_stock=True),
        ]
        
        created_items = []
        for item in search_items:
            created_item = await repository.create(item)
            created_items.append(created_item)
        
        # Act - Search for "laptop"
        laptop_results = await repository.search_by_name("laptop")
        
        # Assert laptop search
        assert len(laptop_results) >= 2  # Should find both laptop items
        laptop_names = [item.name for item in laptop_results]
        assert any("Gaming Laptop" in name for name in laptop_names)
        assert any("Office Laptop" in name for name in laptop_names)
        
        # Act - Search for "gaming"
        gaming_results = await repository.search_by_name("gaming")
        
        # Assert gaming search
        assert len(gaming_results) >= 2  # Should find gaming laptop and gaming mouse
        gaming_names = [item.name for item in gaming_results]
        assert any("Gaming Laptop" in name for name in gaming_names)
        assert any("Gaming Mouse" in name for name in gaming_names)

    @pytest.mark.asyncio
    async def test_search_by_description(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test searching items by description content."""
        # Arrange - Create items with searchable descriptions
        description_items = [
            Item(id=None, name="Product A", description="Professional gaming equipment", price=Decimal("199.99"), in_stock=True),
            Item(id=None, name="Product B", description="Office productivity tools", price=Decimal("89.99"), in_stock=True),
            Item(id=None, name="Product C", description="Gaming accessories and gear", price=Decimal("49.99"), in_stock=False),
        ]
        
        for item in description_items:
            await repository.create(item)
        
        # Act - Search for "gaming" in descriptions
        gaming_desc_results = await repository.search_by_name("gaming")
        
        # Assert
        assert len(gaming_desc_results) >= 2
        descriptions = [item.description for item in gaming_desc_results]
        assert any("gaming equipment" in desc.lower() for desc in descriptions)
        assert any("gaming accessories" in desc.lower() for desc in descriptions)

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test that search is case-insensitive."""
        # Arrange
        test_item = Item(
            id=None,
            name="CaseSensitive Test Item",
            description="Testing CASE sensitivity",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        created_item = await repository.create(test_item)
        
        # Act - Search with different cases
        lower_results = await repository.search_by_name("casesensitive")
        upper_results = await repository.search_by_name("CASESENSITIVE")
        mixed_results = await repository.search_by_name("CaseSensitive")
        
        # Assert - All should return the same item
        assert len(lower_results) >= 1
        assert len(upper_results) >= 1
        assert len(mixed_results) >= 1
        
        # Check that our created item is in all results
        created_id = created_item.id
        assert any(item.id == created_id for item in lower_results)
        assert any(item.id == created_id for item in upper_results)
        assert any(item.id == created_id for item in mixed_results)

    @pytest.mark.asyncio
    async def test_search_no_results(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test searching with query that returns no results."""
        # Act
        results = await repository.search_by_name("nonexistentquerystring123")
        
        # Assert
        assert results == []

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test concurrent repository operations."""
        import asyncio
        
        # Arrange - Create items concurrently
        async def create_item(index):
            item = Item(
                id=None,
                name=f"Concurrent Item {index}",
                description=f"Item created concurrently - {index}",
                price=Decimal(f"{index * 10}.99"),
                in_stock=index % 2 == 0
            )
            return await repository.create(item)
        
        # Act - Create 5 items concurrently
        tasks = [create_item(i) for i in range(1, 6)]
        created_items = await asyncio.gather(*tasks)
        
        # Assert
        assert len(created_items) == 5
        assert all(item.id is not None for item in created_items)
        assert len(set(item.id for item in created_items)) == 5  # All IDs should be unique
        
        # Verify all items can be retrieved
        retrieval_tasks = [repository.get_by_id(item.id) for item in created_items]
        retrieved_items = await asyncio.gather(*retrieval_tasks)
        
        assert all(item is not None for item in retrieved_items)
        assert len(retrieved_items) == 5

    @pytest.mark.asyncio
    async def test_large_dataset_operations(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test repository operations with larger datasets."""
        # Arrange - Create many items
        batch_size = 50
        items_to_create = []
        
        for i in range(batch_size):
            item = Item(
                id=None,
                name=f"Batch Item {i:03d}",
                description=f"Item {i} in large batch test",
                price=Decimal(f"{(i + 1) * 5}.99"),
                in_stock=i % 3 == 0
            )
            items_to_create.append(item)
        
        # Act - Create items in batch
        created_items = []
        for item in items_to_create:
            created_item = await repository.create(item)
            created_items.append(created_item)
        
        # Assert creation
        assert len(created_items) == batch_size
        
        # Act - Retrieve all items
        all_items = await repository.get_all()
        
        # Assert - Our batch items should be included
        created_ids = {item.id for item in created_items}
        all_ids = {item.id for item in all_items}
        assert created_ids.issubset(all_ids)
        
        # Act - Search within the batch
        batch_search_results = await repository.search_by_name("Batch Item")
        
        # Assert search
        assert len(batch_search_results) >= batch_size

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, repository: SQLAlchemyItemRepositoryAdapter):
        """Test that database transactions are properly handled on errors."""
        # This test is more about ensuring the repository doesn't break the session
        # when errors occur, as the actual transaction management is handled at a higher level
        
        # Arrange - Create a valid item first
        valid_item = Item(
            id=None,
            name="Valid Transaction Item",
            description="This should be created successfully",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        created_item = await repository.create(valid_item)
        assert created_item.id is not None
        
        # Act - Attempt to create a duplicate (should raise DuplicateItemError)
        duplicate_item = Item(
            id=None,
            name="Valid Transaction Item",  # Same name
            description="This should fail due to duplicate name",
            price=Decimal("39.99"),
            in_stock=False
        )
        
        with pytest.raises(DuplicateItemError):
            await repository.create(duplicate_item)
        
        # Assert - Repository should still be functional after the error
        # We should be able to perform other operations
        retrieved_item = await repository.get_by_id(created_item.id)
        assert retrieved_item is not None
        assert retrieved_item.name == valid_item.name
        
        # Should be able to create another item with different name
        another_item = Item(
            id=None,
            name="Another Valid Item",
            description="This should work after the error",
            price=Decimal("19.99"),
            in_stock=True
        )
        
        another_created = await repository.create(another_item)
        assert another_created.id is not None