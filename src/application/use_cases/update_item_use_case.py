"""
Use case для обновления существующего элемента.
Инкапсулирует бизнес-логику обновления элемента.
"""

from typing import Optional

from src.application.use_cases.base import BaseUseCase, UseCaseResult
from src.application.dtos.item_dtos import ItemUpdateDTO, ItemResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import ItemNotFoundError, InvalidItemDataError


class UpdateItemRequest:
    """
    Запрос для обновления элемента.
    Инкапсулирует ID элемента и данные для обновления.
    """

    def __init__(self, item_id: int, update_data: ItemUpdateDTO) -> None:
        """
        Инициализация запроса обновления.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            update_data: Данные для обновления элемента
        """
        self.item_id: int = item_id
        self.update_data: ItemUpdateDTO = update_data


class UpdateItemUseCase(BaseUseCase[UpdateItemRequest, ItemResponseDTO]):
    """
    Use case для обновления существующего элемента в системе.
    
    Находит элемент, применяет изменения согласно переданным данным,
    валидирует результат и сохраняет через репозиторий.
    """

    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация use case.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository

    async def validate_request(self, request: UpdateItemRequest) -> Optional[str]:
        """
        Валидация данных для обновления элемента.
        
        Аргументы:
            request: Запрос с данными для обновления
            
        Возвращает:
            None если валидация прошла успешно, иначе сообщение об ошибке
        """
        if request.item_id <= 0:
            return "ID элемента должен быть положительным числом"

        update_data = request.update_data

        # Проверяем, что хотя бы одно поле указано для обновления
        if not any([
            update_data.name is not None,
            update_data.description is not None,
            update_data.price is not None,
            update_data.in_stock is not None
        ]):
            return "Необходимо указать хотя бы одно поле для обновления"

        # Валидация имени, если оно указано
        if update_data.name is not None:
            if not update_data.name.strip():
                return "Название элемента не может быть пустым"
            if len(update_data.name.strip()) > 255:
                return "Название элемента не может превышать 255 символов"

        # Валидация цены, если она указана
        if update_data.price is not None and update_data.price < 0:
            return "Цена не может быть отрицательной"

        return None

    async def execute(self, request: UpdateItemRequest) -> UseCaseResult[ItemResponseDTO]:
        """
        Выполнение обновления элемента.
        
        Аргументы:
            request: Запрос с данными для обновления
            
        Возвращает:
            Результат обновления с данными обновленного элемента
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

            # Получение существующего элемента
            existing_item = await self._item_repository.get_by_id(request.item_id)
            if not existing_item:
                error_result = UseCaseResult.failure_result(
                    error_data=None,  # type: ignore
                    message=f"Элемент с ID {request.item_id} не найден"
                )
                await self.after_execute(request, error_result)
                return error_result

            # Применение изменений
            updated_item = self._apply_updates(existing_item, request.update_data)

            # Сохранение обновленного элемента
            saved_item = await self._item_repository.update(updated_item)
            if not saved_item:
                error_result = UseCaseResult.failure_result(
                    error_data=None,  # type: ignore
                    message=f"Не удалось обновить элемент с ID {request.item_id}"
                )
                await self.after_execute(request, error_result)
                return error_result

            # Преобразование в DTO ответа
            response_dto = self._item_to_response_dto(saved_item)

            result = UseCaseResult.success_result(
                data=response_dto,
                message="Элемент успешно обновлен",
                metadata={"updated_item_id": saved_item.id}
            )

            await self.after_execute(request, result)
            return result

        except (ItemNotFoundError, InvalidItemDataError) as e:
            error_result = UseCaseResult.failure_result(
                error_data=None,  # type: ignore
                message=str(e)
            )
            await self.after_execute(request, error_result)
            return error_result

        except Exception as e:
            return await self.handle_exception(request, e)

    def _apply_updates(self, item: Item, update_data: ItemUpdateDTO) -> Item:
        """
        Применение обновлений к доменной сущности.
        
        Аргументы:
            item: Существующая доменная сущность
            update_data: Данные для обновления
            
        Возвращает:
            Обновленная доменная сущность
            
        Исключения:
            ValueError: При некорректных данных
        """
        # Обновляем только указанные поля
        if update_data.name is not None:
            item.name = update_data.name.strip()

        if update_data.description is not None:
            item.update_description(update_data.description)

        if update_data.price is not None:
            item.update_price(update_data.price)

        if update_data.in_stock is not None:
            if update_data.in_stock:
                item.set_in_stock()
            else:
                item.set_out_of_stock()

        # Валидация обновленной сущности
        item.__post_init__()

        return item

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

    async def before_execute(self, request: UpdateItemRequest) -> None:
        """
        Действия перед выполнением update use case.
        Можно использовать для логирования или дополнительных проверок.
        """
        # Здесь можно добавить логирование
        pass

    async def after_execute(
        self, 
        request: UpdateItemRequest, 
        result: UseCaseResult[ItemResponseDTO]
    ) -> None:
        """
        Действия после выполнения update use case.
        Можно использовать для логирования результата или очистки ресурсов.
        """
        # Здесь можно добавить логирование результата
        pass