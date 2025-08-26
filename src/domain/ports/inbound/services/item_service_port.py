"""
Inbound port interface for Item operations.
Defines the use cases that external actors can request from the domain.
This represents the "driving" side of the hexagonal architecture.
"""

from abc import ABC, abstractmethod
from typing import List

from src.application.dtos.item_dtos import (
    ItemCreateDTO, 
    ItemUpdateDTO, 
    ItemResponseDTO, 
    ItemDeleteResponseDTO,
    ItemSearchDTO
)


class ItemServicePort(ABC):
    """
    Inbound port interface for item-related use cases.
    
    This interface defines what the domain can do when triggered 
    from external actors (web controllers, CLI, message handlers, etc.).
    It represents the application's "API" in the business sense.
    
    Each method represents a specific use case that the domain supports.
    """
    
    @abstractmethod
    async def create_item(self, item_data: ItemCreateDTO) -> ItemResponseDTO:
        """
        Create a new item.
        
        Args:
            item_data: Data for creating the item
            
        Returns:
            Created item response
            
        Raises:
            InvalidItemDataError: If item data is invalid
            DuplicateItemError: If item with same name already exists
        """
        pass
    
    @abstractmethod
    async def get_item_by_id(self, item_id: int) -> ItemResponseDTO:
        """
        Retrieve an item by its ID.
        
        Args:
            item_id: Unique identifier of the item
            
        Returns:
            Item response
            
        Raises:
            ItemNotFoundError: If item is not found
        """
        pass
    
    @abstractmethod
    async def get_all_items(self) -> List[ItemResponseDTO]:
        """
        Retrieve all items.
        
        Returns:
            List of item responses
        """
        pass
    
    @abstractmethod
    async def update_item(self, item_id: int, item_data: ItemUpdateDTO) -> ItemResponseDTO:
        """
        Update an existing item.
        
        Args:
            item_id: Unique identifier of the item
            item_data: Data for updating the item
            
        Returns:
            Updated item response
            
        Raises:
            ItemNotFoundError: If item is not found
            InvalidItemDataError: If item data is invalid
        """
        pass
    
    @abstractmethod
    async def delete_item(self, item_id: int) -> ItemDeleteResponseDTO:
        """
        Delete an item.
        
        Args:
            item_id: Unique identifier of the item
            
        Returns:
            Deletion confirmation response
            
        Raises:
            ItemNotFoundError: If item is not found
        """
        pass
    
    @abstractmethod
    async def search_items(self, search_data: ItemSearchDTO) -> List[ItemResponseDTO]:
        """
        Search items by query.
        
        Args:
            search_data: Search parameters
            
        Returns:
            List of matching item responses
        """
        pass