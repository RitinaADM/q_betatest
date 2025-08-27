"""
Use case для создания нового элемента.
Инкапсулирует бизнес-логику создания элемента.
"""

from typing import Optional

from src.application.use_cases.base import BaseUseCase, UseCaseResult
from src.application.dtos.item_dtos import ItemCreateDTO, ItemResponseDTO
from src.domain.entities.item import Item
from src.domain.ports.outbound.repositories.item_repository import ItemRepository
from src.domain.exceptions import InvalidItemDataError


class CreateItemUseCase(BaseUseCase[ItemCreateDTO, ItemResponseDTO]):
    """
    Use case для создания нового элемента в системе.
    
    Выполняет валидацию данных, создает доменную сущность
    и сохраняет ее через репозиторий.
    """

    def __init__(self, item_repository: ItemRepository) -> None:
        """
        Инициализация use case.
        
        Аргументы:
            item_repository: Репозиторий для работы с элементами
        """
        self._item_repository: ItemRepository = item_repository

    async def validate_request(self, request: ItemCreateDTO) -> Optional[str]:
        """
        Валидация данных для создания элемента.
        
        Аргументы:
            request: Данные для создания элемента
            
        Возвращает:
            None если валидация прошла успешно, иначе сообщение об ошибке
        """
        if not request.name or not request.name.strip():
            return "Название элемента не может быть пустым"
        
        if len(request.name.strip()) > 255:
            return "Название элемента не может превышать 255 символов"
        
        if request.price is not None and request.price < 0:
            return "Цена не может быть отрицательной"
        
        return None

    async def execute(self, request: ItemCreateDTO) -> UseCaseResult[ItemResponseDTO]:
        """
        Выполнение создания элемента.
        
        Аргументы:
            request: Данные для создания элемента
            
        Возвращает:
            Результат создания с данными созданного элемента
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

            # Создание доменной сущности
            item = Item(
                id=None,
                name=request.name.strip(),
                description=request.description,
                price=request.price,
                in_stock=request.in_stock
            )

            # Сохранение через репозиторий
            created_item = await self._item_repository.create(item)

            # Преобразование в DTO ответа
            response_dto = self._item_to_response_dto(created_item)

            result = UseCaseResult.success_result(
                data=response_dto,
                message="Элемент успешно создан",
                metadata={"created_item_id": created_item.id}
            )

            await self.after_execute(request, result)
            return result

        except InvalidItemDataError as e:
            error_result = UseCaseResult.failure_result(
                error_data=None,  # type: ignore
                message=f"Некорректные данные элемента: {str(e)}"
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

    async def before_execute(self, request: ItemCreateDTO) -> None:
        """
        Действия перед выполнением create use case.
        Можно использовать для логирования или дополнительных проверок.
        """
        # Здесь можно добавить логирование
        pass

    async def after_execute(
        self, 
        request: ItemCreateDTO, 
        result: UseCaseResult[ItemResponseDTO]
    ) -> None:
        """
        Действия после выполнения create use case.
        Можно использовать для логирования результата или очистки ресурсов.
        """
        # Здесь можно добавить логирование результата
        pass