"""
Use case для получения элемента по его идентификатору.
Инкапсулирует логику поиска и возврата элемента.
"""

from typing import Optional

from src.application.use_cases.base import BaseUseCase, UseCaseResult
from src.application.dtos.item_dtos import ItemResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import ItemNotFoundError


class GetItemByIdRequest:
    """
    Запрос для получения элемента по ID.
    Инкапсулирует параметры запроса с типизацией.
    """

    def __init__(self, item_id: int) -> None:
        """
        Инициализация запроса.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
        """
        self.item_id: int = item_id


class GetItemByIdUseCase(BaseUseCase[GetItemByIdRequest, ItemResponseDTO]):
    """
    Use case для получения элемента по его идентификатору.
    
    Выполняет поиск элемента в репозитории и возвращает его данные
    или сообщение об отсутствии элемента.
    """

    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация use case.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository

    async def validate_request(self, request: GetItemByIdRequest) -> Optional[str]:
        """
        Валидация параметров запроса.
        
        Аргументы:
            request: Запрос с ID элемента
            
        Возвращает:
            None если валидация прошла успешно, иначе сообщение об ошибке
        """
        if request.item_id <= 0:
            return "ID элемента должен быть положительным числом"
        
        return None

    async def execute(self, request: GetItemByIdRequest) -> UseCaseResult[ItemResponseDTO]:
        """
        Выполнение получения элемента по ID.
        
        Аргументы:
            request: Запрос с ID элемента
            
        Возвращает:
            Результат с данными найденного элемента или ошибкой
        """
        try:
            await self.before_execute(request)
            
            # Валидация входных данных
            validation_error = await self.validate_request(request)
            if validation_error:
                return UseCaseResult.failure_result(
                    error_data=None,  # type: ignore
                    message=validation_error
                )

            # Поиск элемента в репозитории
            item = await self._item_repository.get_by_id(request.item_id)
            
            if not item:
                error_result = UseCaseResult.failure_result(
                    error_data=None,  # type: ignore
                    message=f"Элемент с ID {request.item_id} не найден"
                )
                await self.after_execute(request, error_result)
                return error_result

            # Преобразование в DTO ответа
            response_dto = self._item_to_response_dto(item)

            result = UseCaseResult.success_result(
                data=response_dto,
                message="Элемент успешно найден",
                metadata={"found_item_id": item.id}
            )

            await self.after_execute(request, result)
            return result

        except ItemNotFoundError as e:
            error_result = UseCaseResult.failure_result(
                error_data=None,  # type: ignore
                message=str(e)
            )
            await self.after_execute(request, error_result)
            return error_result

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

    async def before_execute(self, request: GetItemByIdRequest) -> None:
        """
        Действия перед выполнением get by id use case.
        Можно использовать для логирования запроса.
        """
        # Здесь можно добавить логирование запроса
        pass

    async def after_execute(
        self, 
        request: GetItemByIdRequest, 
        result: UseCaseResult[ItemResponseDTO]
    ) -> None:
        """
        Действия после выполнения get by id use case.
        Можно использовать для логирования результата.
        """
        # Здесь можно добавить логирование результата
        pass