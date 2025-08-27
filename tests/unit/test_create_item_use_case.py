"""
Тесты для use case создания элемента.
Демонстрирует тестирование новой архитектуры с полной типизацией.
"""

import pytest
from decimal import Decimal
from typing import Optional
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.create_item_use_case import CreateItemUseCase
from src.application.use_cases.base import UseCaseResult
from src.application.dtos.item_dtos import ItemCreateDTO, ItemResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import InvalidItemDataError


class TestCreateItemUseCase:
    """Тесты для use case создания элемента."""

    @pytest.fixture
    def mock_repository(self) -> ItemRepository:
        """Фикстура для создания мок-репозитория."""
        mock_repo = AsyncMock(spec=ItemRepository)
        return mock_repo

    @pytest.fixture  
    def use_case(self, mock_repository: ItemRepository) -> CreateItemUseCase:
        """Фикстура для создания use case."""
        return CreateItemUseCase(mock_repository)

    @pytest.fixture
    def valid_item_data(self) -> ItemCreateDTO:
        """Фикстура для валидных данных элемента."""
        return ItemCreateDTO(
            name="Тестовый элемент",
            description="Описание тестового элемента",
            price=Decimal("99.99"),
            in_stock=True
        )

    @pytest.mark.asyncio
    async def test_create_item_success(
        self,
        use_case: CreateItemUseCase,
        mock_repository: ItemRepository,
        valid_item_data: ItemCreateDTO
    ) -> None:
        """Тест успешного создания элемента."""
        # Arrange - Подготовка
        created_item = Item(
            id=1,
            name=valid_item_data.name,
            description=valid_item_data.description,
            price=valid_item_data.price,
            in_stock=valid_item_data.in_stock
        )
        mock_repository.create.return_value = created_item

        # Act - Выполнение
        result = await use_case.execute(valid_item_data)

        # Assert - Проверка
        assert result.success is True
        assert result.data is not None
        assert result.data.id == 1
        assert result.data.name == "Тестовый элемент"
        assert result.data.price == Decimal("99.99")
        assert result.data.in_stock is True
        assert "успешно создан" in (result.message or "")

        # Проверяем, что репозиторий был вызван с правильными параметрами
        mock_repository.create.assert_called_once()
        created_item_arg = mock_repository.create.call_args[0][0]
        assert created_item_arg.name == valid_item_data.name
        assert created_item_arg.description == valid_item_data.description
        assert created_item_arg.price == valid_item_data.price
        assert created_item_arg.in_stock == valid_item_data.in_stock

    @pytest.mark.asyncio
    async def test_create_item_with_empty_name_fails(
        self,
        use_case: CreateItemUseCase
    ) -> None:
        """Тест создания элемента с пустым названием."""
        # Arrange
        invalid_data = ItemCreateDTO.model_construct(
            name="",
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )

        # Act
        result = await use_case.execute(invalid_data)

        # Assert
        assert result.success is False
        assert "название" in (result.message or "").lower()
        assert "пустым" in (result.message or "").lower()

    @pytest.mark.asyncio
    async def test_create_item_with_long_name_fails(
        self,
        use_case: CreateItemUseCase
    ) -> None:
        """Тест создания элемента с слишком длинным названием."""
        # Arrange
        invalid_data = ItemCreateDTO.model_construct(
            name="a" * 256,  # Слишком длинное название
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )

        # Act
        result = await use_case.execute(invalid_data)

        # Assert
        assert result.success is False
        assert "255 символов" in (result.message or "")

    @pytest.mark.asyncio
    async def test_create_item_with_negative_price_fails(
        self,
        use_case: CreateItemUseCase
    ) -> None:
        """Тест создания элемента с отрицательной ценой."""
        # Arrange
        invalid_data = ItemCreateDTO.model_construct(
            name="Тестовый элемент",
            description="Описание",
            price=Decimal("-10.00"),  # Отрицательная цена
            in_stock=True
        )

        # Act
        result = await use_case.execute(invalid_data)

        # Assert
        assert result.success is False
        assert "отрицательной" in (result.message or "").lower()

    @pytest.mark.asyncio
    async def test_create_item_repository_error(
        self,
        use_case: CreateItemUseCase,
        mock_repository: ItemRepository,
        valid_item_data: ItemCreateDTO
    ) -> None:
        """Тест обработки ошибки репозитория."""
        # Arrange
        mock_repository.create.side_effect = Exception("Ошибка базы данных")

        # Act
        result = await use_case.execute(valid_item_data)

        # Assert
        assert result.success is False
        assert "ошибка выполнения use case" in (result.message or "").lower()
        assert result.metadata is not None
        assert result.metadata.get("exception_type") == "Exception"

    @pytest.mark.asyncio
    async def test_create_item_validation_before_repository_call(
        self,
        use_case: CreateItemUseCase,
        mock_repository: ItemRepository
    ) -> None:
        """Тест валидации до вызова репозитория."""
        # Arrange
        invalid_data = ItemCreateDTO.model_construct(
            name="   ",  # Только пробелы
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )

        # Act
        result = await use_case.execute(invalid_data)

        # Assert
        assert result.success is False
        # Репозиторий не должен был быть вызван
        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_item_domain_validation_error(
        self,
        use_case: CreateItemUseCase,
        mock_repository: ItemRepository
    ) -> None:
        """Тест обработки ошибки валидации домена."""
        # Arrange
        invalid_data = ItemCreateDTO.model_construct(
            name="Тестовый элемент",
            description="Описание",
            price=Decimal("9999999.99"),  # Превышает максимальную цену
            in_stock=True
        )

        # Act
        result = await use_case.execute(invalid_data)

        # Assert
        assert result.success is False
        assert "цена элемента не может превышать" in (result.message or "").lower()

    @pytest.mark.asyncio
    async def test_create_item_strips_whitespace(
        self,
        use_case: CreateItemUseCase,
        mock_repository: ItemRepository
    ) -> None:
        """Тест обрезки пробелов в названии."""
        # Arrange
        data_with_spaces = ItemCreateDTO(
            name="  Тестовый элемент  ",
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )
        
        created_item = Item(
            id=1,
            name="Тестовый элемент",  # Без пробелов
            description="Описание",
            price=Decimal("10.00"),
            in_stock=True
        )
        mock_repository.create.return_value = created_item

        # Act
        result = await use_case.execute(data_with_spaces)

        # Assert
        assert result.success is True
        # Проверяем, что пробелы были обрезаны
        created_item_arg = mock_repository.create.call_args[0][0]
        assert created_item_arg.name == "Тестовый элемент"