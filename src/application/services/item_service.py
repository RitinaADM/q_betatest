"""
Implementation of the Item Service use cases.
Handles item-related business operations and coordinates with domain and infrastructure.
"""

from typing import List
from decimal import Decimal

from src.domain.ports.inbound.services.item_service_port import ItemServicePort
from src.application.dtos.item_dtos import (
    ItemCreateDTO, 
    ItemUpdateDTO, 
    ItemResponseDTO, 
    ItemDeleteResponseDTO,
    ItemSearchDTO
)
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import ItemNotFoundError, InvalidItemDataError


class ItemService(ItemServicePort):
    """
    Application service implementing item use cases.
    Orchestrates domain logic and coordinates with repositories.
    """
    
    def __init__(self, item_repository: ItemRepository):
        self._item_repository = item_repository
    
    async def create_item(self, item_data: ItemCreateDTO) -> ItemResponseDTO:
        """
        Create a new item.
        
        Args:
            item_data: Data for creating the item
            
        Returns:
            Created item response
            
        Raises:
            InvalidItemDataError: If item data is invalid
        """
        try:
            # Convert DTO to domain entity
            item = Item(
                id=None,
                name=item_data.name,
                description=item_data.description,
                price=item_data.price,
                in_stock=item_data.in_stock
            )
            
            # Create item through repository
            created_item = await self._item_repository.create(item)
            
            # Convert domain entity to response DTO
            return self._item_to_response_dto(created_item)
            
        except ValueError as e:
            raise InvalidItemDataError(str(e))
    
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
        item = await self._item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(item_id)
        
        return self._item_to_response_dto(item)
    
    async def get_all_items(self) -> List[ItemResponseDTO]:
        """
        Retrieve all items.
        
        Returns:
            List of item responses
        """
        items = await self._item_repository.get_all()
        return [self._item_to_response_dto(item) for item in items]
    
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
        # Check if item exists
        existing_item = await self._item_repository.get_by_id(item_id)
        if not existing_item:
            raise ItemNotFoundError(item_id)
        
        try:
            # Update only provided fields
            if item_data.name is not None:
                existing_item.name = item_data.name
            if item_data.description is not None:
                existing_item.update_description(item_data.description)
            if item_data.price is not None:
                existing_item.update_price(item_data.price)
            if item_data.in_stock is not None:
                if item_data.in_stock:
                    existing_item.set_in_stock()
                else:
                    existing_item.set_out_of_stock()
            
            # Validate updated item
            existing_item.__post_init__()
            
            # Update through repository
            updated_item = await self._item_repository.update(existing_item)
            if not updated_item:
                raise ItemNotFoundError(item_id)
            
            return self._item_to_response_dto(updated_item)
            
        except ValueError as e:
            raise InvalidItemDataError(str(e))
    
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
        # Get item before deletion for response
        item = await self._item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(item_id)
        
        # Delete item
        deleted = await self._item_repository.delete(item_id)
        if not deleted:
            raise ItemNotFoundError(item_id)
        
        return ItemDeleteResponseDTO(
            message=f"Item '{item.name}' deleted successfully",
            deleted_item_id=item_id,
            deleted_item_name=item.name
        )
    
    async def search_items(self, search_data: ItemSearchDTO) -> List[ItemResponseDTO]:
        """
        Search items by query.
        
        Args:
            search_data: Search parameters
            
        Returns:
            List of matching item responses
        """
        items = await self._item_repository.search_by_name(search_data.query)
        return [self._item_to_response_dto(item) for item in items]
    
    def _item_to_response_dto(self, item: Item) -> ItemResponseDTO:
        """Convert domain entity to response DTO."""
        if item.id is None:
            raise ValueError("Item ID cannot be None for response DTO")
        
        return ItemResponseDTO(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            in_stock=item.in_stock
        )