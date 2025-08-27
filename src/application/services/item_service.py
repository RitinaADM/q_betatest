"""
Реализация сервиса элементов с использованием use case'ов.
Оркестрирует выполнение бизнес-логики через отдельные use case классы.
"""

from typing import List

from src.domain.ports.inbound.services.item_service_port import ItemServicePort
from src.application.dtos.item_dtos import (
    ItemCreateDTO, 
    ItemUpdateDTO, 
    ItemResponseDTO, 
    ItemDeleteResponseDTO,
    ItemSearchDTO
)
from src.domain.ports.outbound.repositories.item_repository import ItemRepository

# Импорт всех use case'ов
from src.application.use_cases.create_item_use_case import CreateItemUseCase
from src.application.use_cases.get_item_by_id_use_case import (
    GetItemByIdUseCase, 
    GetItemByIdRequest
)
from src.application.use_cases.get_all_items_use_case import (
    GetAllItemsUseCase, 
    GetAllItemsRequest
)
from src.application.use_cases.update_item_use_case import (
    UpdateItemUseCase, 
    UpdateItemRequest
)
from src.application.use_cases.delete_item_use_case import (
    DeleteItemUseCase, 
    DeleteItemRequest
)
from src.application.use_cases.search_items_use_case import SearchItemsUseCase


class ItemService(ItemServicePort):
    """
    Сервис приложения для работы с элементами.
    Оркестрирует выполнение use case'ов и предоставляет единый интерфейс для контроллеров.
    
    Сервис больше не содержит бизнес-логику напрямую, а делегирует выполнение
    соответствующим use case'ам, что обеспечивает лучшую модульность и тестируемость.
    """
    
    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация сервиса и всех use case'ов.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository
        
        # Инициализация всех use case'ов
        self._create_item_use_case = CreateItemUseCase(item_repository)
        self._get_item_by_id_use_case = GetItemByIdUseCase(item_repository)
        self._get_all_items_use_case = GetAllItemsUseCase(item_repository)
        self._update_item_use_case = UpdateItemUseCase(item_repository)
        self._delete_item_use_case = DeleteItemUseCase(item_repository)
        self._search_items_use_case = SearchItemsUseCase(item_repository)
    
    async def create_item(self, item_data: ItemCreateDTO) -> ItemResponseDTO:
        """
        Создание нового элемента.
        
        Аргументы:
            item_data: Данные для создания элемента
            
        Возвращает:
            Ответ с данными созданного элемента
            
        Исключения:
            InvalidItemDataError: При некорректных данных элемента
        """
        result = await self._create_item_use_case.execute(item_data)
        
        if not result.success:
            from src.domain.exceptions import InvalidItemDataError
            raise InvalidItemDataError(result.message or "Ошибка создания элемента")
        
        return result.data
    
    async def get_item_by_id(self, item_id: int) -> ItemResponseDTO:
        """
        Получение элемента по его идентификатору.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            
        Возвращает:
            Ответ с данными элемента
            
        Исключения:
            ItemNotFoundError: Если элемент не найден
        """
        request = GetItemByIdRequest(item_id)
        result = await self._get_item_by_id_use_case.execute(request)
        
        if not result.success:
            from src.domain.exceptions import ItemNotFoundError
            raise ItemNotFoundError(item_id)
        
        return result.data
    
    async def get_all_items(self) -> List[ItemResponseDTO]:
        """
        Получение всех элементов.
        
        Возвращает:
            Список ответов с данными всех элементов
        """
        request = GetAllItemsRequest()
        result = await self._get_all_items_use_case.execute(request)
        
        # Для get_all операция всегда должна возвращать список (даже пустой)
        return result.data or []
    
    async def update_item(self, item_id: int, item_data: ItemUpdateDTO) -> ItemResponseDTO:
        """
        Обновление существующего элемента.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            item_data: Данные для обновления элемента
            
        Возвращает:
            Ответ с данными обновленного элемента
            
        Исключения:
            ItemNotFoundError: Если элемент не найден
            InvalidItemDataError: При некорректных данных элемента
        """
        request = UpdateItemRequest(item_id, item_data)
        result = await self._update_item_use_case.execute(request)
        
        if not result.success:
            # Определяем тип исключения на основе сообщения
            if "не найден" in (result.message or ""):
                from src.domain.exceptions import ItemNotFoundError
                raise ItemNotFoundError(item_id)
            else:
                from src.domain.exceptions import InvalidItemDataError
                raise InvalidItemDataError(result.message or "Ошибка обновления элемента")
        
        return result.data
    
    async def delete_item(self, item_id: int) -> ItemDeleteResponseDTO:
        """
        Удаление элемента.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            
        Возвращает:
            Подтверждение удаления элемента
            
        Исключения:
            ItemNotFoundError: Если элемент не найден
        """
        request = DeleteItemRequest(item_id)
        result = await self._delete_item_use_case.execute(request)
        
        if not result.success:
            from src.domain.exceptions import ItemNotFoundError
            raise ItemNotFoundError(item_id)
        
        return result.data
    
    async def search_items(self, search_data: ItemSearchDTO) -> List[ItemResponseDTO]:
        """
        Поиск элементов по запросу.
        
        Аргументы:
            search_data: Параметры поиска
            
        Возвращает:
            Список найденных элементов
        """
        result = await self._search_items_use_case.execute(search_data)
        
        # Для поиска всегда возвращаем список (даже пустой)
        return result.data or []