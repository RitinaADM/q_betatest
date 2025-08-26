from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.ports.inbound.services.item_service_port import ItemServicePort
from src.application.services.item_service import ItemService
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.infrastructure.adapters.outbound.database.sql.item_repository_adapter import SQLAlchemyItemRepositoryAdapter
from src.application.dtos.item_dtos import (
    ItemCreateDTO,
    ItemUpdateDTO,
    ItemResponseDTO,
    ItemDeleteResponseDTO,
    ItemSearchDTO
)
from src.domain.exceptions import ItemNotFoundError, InvalidItemDataError
from src.infrastructure.database.config import get_async_session


router = APIRouter(prefix="/items", tags=["items"])


async def get_item_service(session: AsyncSession = Depends(get_async_session)) -> ItemServicePort:
    """Factory function to create ItemServicePort with proper dependency injection."""
    repository: ItemRepository = SQLAlchemyItemRepositoryAdapter(session)
    return ItemService(repository)


@router.post("/", response_model=ItemResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreateDTO,
    item_service: ItemServicePort = Depends(get_item_service)
) -> ItemResponseDTO:
    """Create a new item."""
    try:
        return await item_service.create_item(item_data)
    except InvalidItemDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ItemResponseDTO])
async def get_all_items(
    item_service: ItemServicePort = Depends(get_item_service)
) -> List[ItemResponseDTO]:
    """Retrieve all items."""
    return await item_service.get_all_items()


@router.get("/{item_id}", response_model=ItemResponseDTO)
async def get_item(
    item_id: int,
    item_service: ItemServicePort = Depends(get_item_service)
) -> ItemResponseDTO:
    """Retrieve an item by its ID."""
    try:
        return await item_service.get_item_by_id(item_id)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )


@router.put("/{item_id}", response_model=ItemResponseDTO)
async def update_item(
    item_id: int,
    item_data: ItemUpdateDTO,
    item_service: ItemServicePort = Depends(get_item_service)
) -> ItemResponseDTO:
    """Update an existing item."""
    try:
        return await item_service.update_item(item_id, item_data)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    except InvalidItemDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{item_id}", response_model=ItemDeleteResponseDTO)
async def delete_item(
    item_id: int,
    item_service: ItemServicePort = Depends(get_item_service)
) -> ItemDeleteResponseDTO:
    """Delete an item."""
    try:
        return await item_service.delete_item(item_id)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )


@router.get("/search/{query}", response_model=List[ItemResponseDTO])
async def search_items(
    query: str,
    item_service: ItemServicePort = Depends(get_item_service)
) -> List[ItemResponseDTO]:
    """Search items by query string."""
    search_data = ItemSearchDTO(query=query)
    return await item_service.search_items(search_data)