from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.item import Item


class ItemRepository(ABC):
    """
    Abstract repository interface for Item entity.
    Defines the contract for data persistence operations.
    """
    
    @abstractmethod
    async def create(self, item: Item) -> Item:
        """
        Create a new item in the repository.
        
        Args:
            item: Item entity to create
            
        Returns:
            Created item with assigned ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """
        Retrieve an item by its ID.
        
        Args:
            item_id: Unique identifier of the item
            
        Returns:
            Item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Item]:
        """
        Retrieve all items from the repository.
        
        Returns:
            List of all items
        """
        pass
    
    @abstractmethod
    async def update(self, item: Item) -> Optional[Item]:
        """
        Update an existing item in the repository.
        
        Args:
            item: Item entity with updated data
            
        Returns:
            Updated item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """
        Delete an item from the repository.
        
        Args:
            item_id: Unique identifier of the item to delete
            
        Returns:
            True if item was deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def search_by_name(self, query: str) -> List[Item]:
        """
        Search items by name containing the query string.
        
        Args:
            query: Search query string
            
        Returns:
            List of items matching the search criteria
        """
        pass