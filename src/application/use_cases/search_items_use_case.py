"""
Use case для поиска элементов по критериям.
Инкапсулирует бизнес-логику поиска элементов.
"""

from typing import List, Optional

from src.application.use_cases.base import BaseUseCase, UseCaseResult
from src.application.dtos.item_dtos import ItemSearchDTO, ItemResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository


class SearchItemsUseCase(BaseUseCase[ItemSearchDTO, List[ItemResponseDTO]]):
    """
    Use case для поиска элементов по заданным критериям.
    
    Выполняет поиск элементов в репозитории по переданному запросу
    и возвращает список найденных элементов.
    """

    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация use case.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository

    async def validate_request(self, request: ItemSearchDTO) -> Optional[str]:
        """
        Валидация поискового запроса.
        
        Аргументы:
            request: Данные для поиска элементов
            
        Возвращает:
            None если валидация прошла успешно, иначе сообщение об ошибке
        """
        if not request.query or not request.query.strip():
            return "Поисковый запрос не может быть пустым"

        if len(request.query.strip()) < 2:
            return "Поисковый запрос должен содержать минимум 2 символа"

        if len(request.query.strip()) > 100:
            return "Поисковый запрос не может превышать 100 символов"

        return None

    async def execute(self, request: ItemSearchDTO) -> UseCaseResult[List[ItemResponseDTO]]:
        """
        Выполнение поиска элементов.
        
        Аргументы:
            request: Данные для поиска элементов
            
        Возвращает:
            Результат с найденными элементами
        """
        try:
            await self.before_execute(request)
            
            # Валидация входных данных
            validation_error = await self.validate_request(request)
            if validation_error:
                return UseCaseResult.failure_result(
                    error_data=[],  # Возвращаем пустой список для поиска
                    message=validation_error
                )

            # Нормализация поискового запроса
            normalized_query = request.query.strip().lower()

            # Выполнение поиска через репозиторий
            found_items = await self._item_repository.search_by_name(normalized_query)

            # Преобразование в DTO ответов
            response_dtos = [
                self._item_to_response_dto(item) for item in found_items
            ]

            # Определение сообщения результата
            if response_dtos:
                message = f"Найдено {len(response_dtos)} элементов по запросу '{request.query}'"
            else:
                message = f"Элементы по запросу '{request.query}' не найдены"

            result = UseCaseResult.success_result(
                data=response_dtos,
                message=message,
                metadata={
                    "search_query": request.query,
                    "normalized_query": normalized_query,
                    "found_count": len(response_dtos),
                    "has_results": len(response_dtos) > 0
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

    async def before_execute(self, request: ItemSearchDTO) -> None:
        """
        Действия перед выполнением search use case.
        Можно использовать для логирования поискового запроса.
        """
        # Здесь можно добавить логирование поискового запроса
        pass

    async def after_execute(
        self, 
        request: ItemSearchDTO, 
        result: UseCaseResult[List[ItemResponseDTO]]
    ) -> None:
        """
        Действия после выполнения search use case.
        Можно использовать для логирования результатов поиска.
        """
        # Здесь можно добавить логирование результатов поиска
        pass

    async def handle_exception(
        self, 
        request: ItemSearchDTO, 
        exception: Exception
    ) -> UseCaseResult[List[ItemResponseDTO]]:
        """
        Обработка исключений для поискового use case.
        Возвращает пустой список вместо None для соответствия типу возврата.
        
        Аргументы:
            request: Входные данные use case
            exception: Возникшее исключение
            
        Возвращает:
            UseCaseResult с пустым списком и информацией об ошибке
        """
        error_message = f"Ошибка выполнения поиска: {str(exception)}"
        return UseCaseResult.failure_result(
            error_data=[],  # Возвращаем пустой список для типобезопасности
            message=error_message,
            metadata={"exception_type": type(exception).__name__}
        )