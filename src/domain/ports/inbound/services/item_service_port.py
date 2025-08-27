"""
Интерфейс входящего порта для операций с элементами.
Определяет use case'ы, которые внешние акторы могут запросить у домена.
Представляет "управляющую" сторону гексагональной архитектуры.
"""

from abc import ABC, abstractmethod
from typing import List, Coroutine, Any, Protocol

from src.application.dtos.item_dtos import (
    ItemCreateDTO, 
    ItemUpdateDTO, 
    ItemResponseDTO, 
    ItemDeleteResponseDTO,
    ItemSearchDTO
)


class ItemServicePort(Protocol):
    """
    Протокол входящего порта для use case'ов, связанных с элементами.
    
    Этот интерфейс определяет, что может делать домен при активации 
    внешними акторами (веб-контроллеры, CLI, обработчики сообщений и т.д.).
    Он представляет "API" приложения в бизнес-смысле.
    
    Каждый метод представляет конкретный use case, который поддерживает домен.
    """
    
    async def create_item(self, item_data: ItemCreateDTO) -> ItemResponseDTO:
        """
        Создание нового элемента.
        
        Аргументы:
            item_data: Данные для создания элемента
            
        Возвращает:
            Ответ с данными созданного элемента
            
        Исключения:
            InvalidItemDataError: При некорректных данных элемента
            DuplicateItemError: При существовании элемента с таким же названием
        """
        ...
    
    async def get_item_by_id(self, item_id: int) -> ItemResponseDTO:
        """
        Получение элемента по его идентификатору.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            
        Возвращает:
            Ответ с данными элемента
            
        Исключения:
            ItemNotFoundError: При отсутствии элемента
        """
        ...
    
    async def get_all_items(self) -> List[ItemResponseDTO]:
        """
        Получение всех элементов.
        
        Возвращает:
            Список ответов с данными всех элементов
        """
        ...
    
    async def update_item(self, item_id: int, item_data: ItemUpdateDTO) -> ItemResponseDTO:
        """
        Обновление существующего элемента.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            item_data: Данные для обновления элемента
            
        Возвращает:
            Ответ с данными обновленного элемента
            
        Исключения:
            ItemNotFoundError: При отсутствии элемента
            InvalidItemDataError: При некорректных данных элемента
        """
        ...
    
    async def delete_item(self, item_id: int) -> ItemDeleteResponseDTO:
        """
        Удаление элемента.
        
        Аргументы:
            item_id: Уникальный идентификатор элемента
            
        Возвращает:
            Подтверждение удаления элемента
            
        Исключения:
            ItemNotFoundError: При отсутствии элемента
        """
        ...
    
    async def search_items(self, search_data: ItemSearchDTO) -> List[ItemResponseDTO]:
        """
        Поиск элементов по запросу.
        
        Аргументы:
            search_data: Параметры поиска
            
        Возвращает:
            Список найденных элементов
        """
        ...