"""
Тесты для обновленного ItemService с use case архитектурой.
Демонстрирует интеграционное тестирование сервиса и use case'ов.
"""

import pytest
from decimal import Decimal
from typing import List
from unittest.mock import AsyncMock, Mock, MagicMock

from src.application.services.item_service import ItemService
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


class TestItemServiceWithUseCases:
    """Тесты для ItemService с новой use case архитектурой."""

    @pytest.fixture
    def mock_repository(self) -> ItemRepository:
        """Фикстура для создания мок-репозитория."""
        mock_repo = AsyncMock(spec=ItemRepository)
        return mock_repo

    @pytest.fixture
    def service(self, mock_repository: ItemRepository) -> ItemService:
        """Фикстура для создания сервиса."""
        return ItemService(mock_repository)

    @pytest.fixture
    def sample_item(self) -> Item:
        """Фикстура для тестового элемента."""
        return Item(
            id=1,
            name="Тестовый элемент",
            description="Описание тестового элемента",
            price=Decimal("99.99"),
            in_stock=True
        )

    @pytest.mark.asyncio
    async def test_create_item_success(
        self,
        service: ItemService,
        mock_repository: ItemRepository,
        sample_item: Item
    ) -> None:
        """Тест успешного создания элемента через сервис."""
        # Arrange
        create_data = ItemCreateDTO(
            name="Тестовый элемент",
            description="Описание тестового элемента",
            price=Decimal("99.99"),
            in_stock=True
        )
        mock_repository.create.return_value = sample_item

        # Act
        result = await service.create_item(create_data)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.id == 1
        assert result.name == "Тестовый элемент"
        assert result.price == Decimal("99.99")
        assert result.in_stock is True

    @pytest.mark.asyncio
    async def test_create_item_invalid_data_raises_exception(
        self,
        service: ItemService
    ) -> None:
        """Тест обработки некорректных данных при создании."""
        # Arrange
        invalid_data = ItemCreateDTO.model_construct(
            name="",  # Пустое название
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )

        # Act & Assert
        with pytest.raises(InvalidItemDataError) as exc_info:
            await service.create_item(invalid_data)
        
        assert "название" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_item_by_id_success(
        self,
        service: ItemService,
        mock_repository: ItemRepository,
        sample_item: Item
    ) -> None:
        """Тест успешного получения элемента по ID."""
        # Arrange
        mock_repository.get_by_id.return_value = sample_item

        # Act
        result = await service.get_item_by_id(1)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.id == 1
        assert result.name == "Тестовый элемент"
        mock_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found_raises_exception(
        self,
        service: ItemService,
        mock_repository: ItemRepository
    ) -> None:
        """Тест обработки отсутствующего элемента."""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ItemNotFoundError):
            await service.get_item_by_id(999)

    @pytest.mark.asyncio
    async def test_get_item_by_id_invalid_id_raises_exception(
        self,
        service: ItemService
    ) -> None:
        """Тест обработки некорректного ID."""
        # Act & Assert
        with pytest.raises(ItemNotFoundError):
            await service.get_item_by_id(-1)

    @pytest.mark.asyncio
    async def test_get_all_items_success(
        self,
        service: ItemService,
        mock_repository: ItemRepository,
        sample_item: Item
    ) -> None:
        """Тест успешного получения всех элементов."""
        # Arrange
        items = [sample_item, sample_item]
        mock_repository.get_all.return_value = items

        # Act
        result = await service.get_all_items()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, ItemResponseDTO) for item in result)
        mock_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_items_empty_list(
        self,
        service: ItemService,
        mock_repository: ItemRepository
    ) -> None:
        """Тест получения пустого списка элементов."""
        # Arrange
        mock_repository.get_all.return_value = []

        # Act
        result = await service.get_all_items()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_update_item_success(
        self,
        service: ItemService,
        mock_repository: ItemRepository,
        sample_item: Item
    ) -> None:
        """Тест успешного обновления элемента."""
        # Arrange
        update_data = ItemUpdateDTO(
            name="Обновленное название",
            price=Decimal("199.99")
        )
        
        updated_item = Item(
            id=1,
            name="Обновленное название",
            description="Описание тестового элемента",
            price=Decimal("199.99"),
            in_stock=True
        )
        
        mock_repository.get_by_id.return_value = sample_item
        mock_repository.update.return_value = updated_item

        # Act
        result = await service.update_item(1, update_data)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.name == "Обновленное название"
        assert result.price == Decimal("199.99")

    @pytest.mark.asyncio
    async def test_update_item_not_found_raises_exception(
        self,
        service: ItemService,
        mock_repository: ItemRepository
    ) -> None:
        """Тест обновления несуществующего элемента."""
        # Arrange
        update_data = ItemUpdateDTO(name="Новое название")
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ItemNotFoundError):
            await service.update_item(999, update_data)

    @pytest.mark.asyncio
    async def test_delete_item_success(
        self,
        service: ItemService,
        mock_repository: ItemRepository,
        sample_item: Item
    ) -> None:
        """Тест успешного удаления элемента."""
        # Arrange
        mock_repository.get_by_id.return_value = sample_item
        mock_repository.delete.return_value = True

        # Act
        result = await service.delete_item(1)

        # Assert
        assert isinstance(result, ItemDeleteResponseDTO)
        assert result.deleted_item_id == 1
        assert result.deleted_item_name == "Тестовый элемент"
        assert "успешно удален" in result.message

    @pytest.mark.asyncio
    async def test_delete_item_not_found_raises_exception(
        self,
        service: ItemService,
        mock_repository: ItemRepository
    ) -> None:
        """Тест удаления несуществующего элемента."""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ItemNotFoundError):
            await service.delete_item(999)

    @pytest.mark.asyncio
    async def test_search_items_success(
        self,
        service: ItemService,
        mock_repository: ItemRepository,
        sample_item: Item
    ) -> None:
        """Тест успешного поиска элементов."""
        # Arrange
        search_data = ItemSearchDTO(query="тест")
        found_items = [sample_item]
        mock_repository.search_by_name.return_value = found_items

        # Act
        result = await service.search_items(search_data)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ItemResponseDTO)
        assert result[0].name == "Тестовый элемент"

    @pytest.mark.asyncio
    async def test_search_items_no_results(
        self,
        service: ItemService,
        mock_repository: ItemRepository
    ) -> None:
        """Тест поиска без результатов."""
        # Arrange
        search_data = ItemSearchDTO(query="несуществующий")
        mock_repository.search_by_name.return_value = []

        # Act
        result = await service.search_items(search_data)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_service_orchestrates_use_cases_properly(
        self,
        service: ItemService,
        mock_repository: ItemRepository
    ) -> None:
        """Тест правильной оркестрации use case'ов сервисом."""
        # Arrange
        create_data = ItemCreateDTO(
            name="Тест",
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )
        created_item = Item(
            id=1,
            name="Тест",
            description="Описание", 
            price=Decimal("10.00"),
            in_stock=True
        )
        mock_repository.create.return_value = created_item

        # Act
        result = await service.create_item(create_data)

        # Assert
        # Проверяем, что сервис действительно использует use case
        # (а не вызывает репозиторий напрямую как раньше)
        assert hasattr(service, '_create_item_use_case')
        assert hasattr(service, '_get_item_by_id_use_case')
        assert hasattr(service, '_get_all_items_use_case')
        assert hasattr(service, '_update_item_use_case')
        assert hasattr(service, '_delete_item_use_case')
        assert hasattr(service, '_search_items_use_case')
        
        # Результат должен быть корректным
        assert isinstance(result, ItemResponseDTO)
        assert result.name == "Тест"