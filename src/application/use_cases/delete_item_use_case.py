"""
Use case для удаления элемента из системы.
Инкапсулирует бизнес-логику удаления элемента.
"""

from typing import Optional

from src.application.use_cases.base import BaseUseCase, UseCaseResult
from src.application.dtos.item_dtos import ItemDeleteResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import ItemNotFoundError


class DeleteItemRequest:
    """
    Запрос для удаления элемента.
    Инкапсулирует ID элемента для удаления.
    """

    def __init__(self, item_id: int) -> None:
        """
        Инициализация запроса удаления.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента для удаления
        """
        self.item_id: int = item_id


class DeleteItemUseCase(BaseUseCase[DeleteItemRequest, ItemDeleteResponseDTO]):
    """
    Use case для удаления элемента из системы.
    
    Проверяет существование элемента, выполняет удаление через репозиторий
    и возвращает подтверждение об успешном удалении.
    """

    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация use case.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository

    async def validate_request(self, request: DeleteItemRequest) -> Optional[str]:
        """
        Валидация запроса на удаление.
        
        Аргументы:
            request: Запрос с ID элемента для удаления
            
        Возвращает:
            None если валидация прошла успешно, иначе сообщение об ошибке
        """
        if request.item_id <= 0:
            return "ID элемента должен быть положительным числом"
        
        return None

    async def execute(self, request: DeleteItemRequest) -> UseCaseResult[ItemDeleteResponseDTO]:
        """
        Выполнение удаления элемента.
        
        Аргументы:
            request: Запрос с ID элемента для удаления
            
        Возвращает:
            Результат удаления с подтверждением операции
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

            # Получение элемента перед удалением для формирования ответа
            item_to_delete = await self._item_repository.get_by_id(request.item_id)
            if not item_to_delete:
                error_result = UseCaseResult.failure_result(
                    error_data=None,  # type: ignore
                    message=f"Элемент с ID {request.item_id} не найден"
                )
                await self.after_execute(request, error_result)
                return error_result

            # Выполнение удаления
            deleted = await self._item_repository.delete(request.item_id)
            if not deleted:
                error_result = UseCaseResult.failure_result(
                    error_data=None,  # type: ignore
                    message=f"Не удалось удалить элемент с ID {request.item_id}"
                )
                await self.after_execute(request, error_result)
                return error_result

            # Создание DTO ответа
            response_dto = self._create_delete_response_dto(item_to_delete)

            result = UseCaseResult.success_result(
                data=response_dto,
                message="Элемент успешно удален",
                metadata={
                    "deleted_item_id": request.item_id,
                    "deleted_item_name": item_to_delete.name
                }
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

    def _create_delete_response_dto(self, deleted_item: Item) -> ItemDeleteResponseDTO:
        """
        Создание DTO ответа для удаления.
        
        Аргументы:
            deleted_item: Удаленная доменная сущность
            
        Возвращает:
            DTO ответа с информацией об удалении
            
        Исключения:
            ValueError: Если ID элемента равен None
        """
        if deleted_item.id is None:
            raise ValueError("ID элемента не может быть None для DTO ответа")

        return ItemDeleteResponseDTO(
            message=f"Элемент '{deleted_item.name}' успешно удален",
            deleted_item_id=deleted_item.id,
            deleted_item_name=deleted_item.name
        )

    async def before_execute(self, request: DeleteItemRequest) -> None:
        """
        Действия перед выполнением delete use case.
        Можно использовать для логирования или дополнительных проверок.
        """
        # Здесь можно добавить логирование запроса на удаление
        pass

    async def after_execute(
        self, 
        request: DeleteItemRequest, 
        result: UseCaseResult[ItemDeleteResponseDTO]
    ) -> None:
        """
        Действия после выполнения delete use case.
        Можно использовать для логирования результата или аудита.
        """
        # Здесь можно добавить логирование результата удаления
        pass