from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.exc import IntegrityError

from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import DuplicateItemError
from src.infrastructure.database.models import ItemModel


class SQLAlchemyItemRepositoryAdapter(ItemRepository):
    """
    SQLAlchemy implementation of ItemRepository.
    Handles data persistence using SQLAlchemy ORM.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, item: Item) -> Item:
        """
        Create a new item in the database.
        
        Args:
            item: Item entity to create
            
        Returns:
            Created item with assigned ID
            
        Raises:
            DuplicateItemError: If item with same name already exists
        """
        try:
            # Check for existing item with same name first
            existing = await self.exists_by_name(item.name)
            if existing:
                raise DuplicateItemError(item.name)
            
            # Convert domain entity to database model
            db_item = ItemModel.from_domain_entity(item)
            
            # Add to session and flush to get ID
            self._session.add(db_item)
            await self._session.flush()
            await self._session.refresh(db_item)
            
            # Convert back to domain entity
            return db_item.to_domain_entity()
            
        except IntegrityError as e:
            await self._session.rollback()
            # Check if it's a duplicate name constraint violation
            if "UNIQUE constraint failed" in str(e) or "name" in str(e).lower():
                raise DuplicateItemError(item.name)
            raise  # Re-raise other integrity errors
    
    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """
        Retrieve an item by its ID.
        
        Args:
            item_id: Unique identifier of the item
            
        Returns:
            Item if found, None otherwise
        """
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        result = await self._session.execute(stmt)
        db_item = result.scalar_one_or_none()
        
        return db_item.to_domain_entity() if db_item else None
    
    async def get_all(self) -> List[Item]:
        """
        Retrieve all items from the database.
        
        Returns:
            List of all items
        """
        stmt = select(ItemModel).order_by(ItemModel.id)
        result = await self._session.execute(stmt)
        db_items = result.scalars().all()
        
        return [db_item.to_domain_entity() for db_item in db_items]
    
    async def update(self, item: Item) -> Optional[Item]:
        """
        Update an existing item in the database.
        
        Args:
            item: Item entity with updated data
            
        Returns:
            Updated item if found, None otherwise
        """
        stmt = select(ItemModel).where(ItemModel.id == item.id)
        result = await self._session.execute(stmt)
        db_item = result.scalar_one_or_none()
        
        if not db_item:
            return None
        
        # Update the database model with domain entity data
        db_item.update_from_domain_entity(item)
        
        # Flush changes and refresh
        await self._session.flush()
        await self._session.refresh(db_item)
        
        return db_item.to_domain_entity()
    
    async def delete(self, item_id: int) -> bool:
        """
        Delete an item from the database.
        
        Args:
            item_id: Unique identifier of the item to delete
            
        Returns:
            True if item was deleted, False if not found
        """
        stmt = delete(ItemModel).where(ItemModel.id == item_id)
        result = await self._session.execute(stmt)
        
        return result.rowcount > 0
    
    async def search_by_name(self, query: str) -> List[Item]:
        """
        Search items by name containing the query string.
        
        Args:
            query: Search query string
            
        Returns:
            List of items matching the search criteria
        """
        # Case-insensitive search in name and description
        search_pattern = f"%{query.lower()}%"
        
        stmt = select(ItemModel).where(
            or_(
                ItemModel.name.ilike(search_pattern),
                ItemModel.description.ilike(search_pattern)
            )
        ).order_by(ItemModel.name)
        
        result = await self._session.execute(stmt)
        db_items = result.scalars().all()
        
        return [db_item.to_domain_entity() for db_item in db_items]
    
    async def exists_by_name(self, name: str) -> bool:
        """
        Check if an item with the given name exists.
        
        Args:
            name: Item name to check
            
        Returns:
            True if item exists, False otherwise
        """
        stmt = select(ItemModel.id).where(ItemModel.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None