"""
Экспорт всех use case'ов приложения.
Предоставляет централизованный доступ к бизнес-логике.
"""

from src.application.use_cases.base import (
    BaseUseCase,
    SyncBaseUseCase,
    UseCaseResult
)
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

__all__ = [
    # Базовые классы
    'BaseUseCase',
    'SyncBaseUseCase',
    'UseCaseResult',
    
    # Use case'ы для элементов
    'CreateItemUseCase',
    'GetItemByIdUseCase',
    'GetAllItemsUseCase',
    'UpdateItemUseCase',
    'DeleteItemUseCase',
    'SearchItemsUseCase',
    
    # Запросы для use case'ов
    'GetItemByIdRequest',
    'GetAllItemsRequest',
    'UpdateItemRequest',
    'DeleteItemRequest',
]