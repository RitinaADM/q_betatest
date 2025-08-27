"""
Use case для получения всех элементов из системы.
Инкапсулирует логику получения полного списка элементов.
"""

from typing import List, Optional

from src.application.use_cases.base import BaseUseCase, UseCaseResult
from src.application.dtos.item_dtos import ItemResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository


class GetAllItemsRequest:
    """
    Запрос для получения всех элементов.
    Пустой класс для соблюдения единообразия интерфейса use case.
    """

    def __init__(self) -> None:
        """Инициализация пустого запроса."""
        pass


class GetAllItemsUseCase(BaseUseCase[GetAllItemsRequest, List[ItemResponseDTO]]):
    """
    Use case для получения всех элементов из системы.
    
    Получает полный список элементов из репозитория и преобразует
    их в список DTO для ответа.
    """

    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация use case.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository

    async def validate_request(self, request: GetAllItemsRequest) -> Optional[str]:
        """
        Валидация запроса (для этого use case всегда успешна).
        
        Аргументы:
            request: Пустой запрос
            
        Возвращает:
            None, так как запрос не содержит параметров для валидации
        """
        return None

    async def execute(self, request: GetAllItemsRequest) -> UseCaseResult[List[ItemResponseDTO]]:
        """
        Выполнение получения всех элементов.
        
        Аргументы:
            request: Пустой запрос
            
        Возвращает:
            Результат со списком всех элементов
        """
        try:
            await self.before_execute(request)

            # Получение всех элементов из репозитория
            items = await self._item_repository.get_all()

            # Преобразование в список DTO ответов
            response_dtos = [
                self._item_to_response_dto(item) for item in items
            ]

            result = UseCaseResult.success_result(
                data=response_dtos,
                message=f"Найдено {len(response_dtos)} элементов",
                metadata={
                    "total_count": len(response_dtos),
                    "has_items": len(response_dtos) > 0
                }
            )

            await self.after_execute(request, result)
            return result

        except Exception as e:
            return await self.handle_exception(request, e)

    def _item_to_response_dto(self, item: Item) -> ItemResponseDTO:
        """
        Преобразование доменной сущности в DTO ответа.
        
        Аргументы:
            item: Доменная сущность элемента
            
        Возвращает:
            DTO ответа с данными элемента
            
        Исключения:
            ValueError: Если ID элемента равен None
        """
        if item.id is None:
            raise ValueError("ID элемента не может быть None для DTO ответа")

        return ItemResponseDTO(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            in_stock=item.in_stock
        )

    async def before_execute(self, request: GetAllItemsRequest) -> None:
        """
        Действия перед выполнением get all use case.
        Можно использовать для логирования начала операции.
        """
        # Здесь можно добавить логирование начала операции
        pass

    async def after_execute(
        self, 
        request: GetAllItemsRequest, 
        result: UseCaseResult[List[ItemResponseDTO]]
    ) -> None:
        """
        Действия после выполнения get all use case.
        Можно использовать для логирования результата.
        """
        # Здесь можно добавить логирование результата
        pass

    async def handle_exception(
        self, 
        request: GetAllItemsRequest, 
        exception: Exception
    ) -> UseCaseResult[List[ItemResponseDTO]]:
        """
        Обработка исключений для get all use case.
        Возвращает пустой список вместо None для соответствия типу возврата.
        
        Аргументы:
            request: Входные данные use case
            exception: Возникшее исключение
            
        Возвращает:
            UseCaseResult с пустым списком и информацией об ошибке
        """
        error_message = f"Ошибка получения списка элементов: {str(exception)}"
        return UseCaseResult.failure_result(
            error_data=[],  # Возвращаем пустой список для типобезопасности
            message=error_message,
            metadata={"exception_type": type(exception).__name__}
        )