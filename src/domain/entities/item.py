"""
Доменная сущность элемента с полной типизацией.
Содержит бизнес-логику, правила валидации и инварианты.
"""

from dataclasses import dataclass
from typing import Optional, Union, Any
from decimal import Decimal


@dataclass
class Item:
    """
    Доменная сущность, представляющая бизнес-элемент.
    Содержит всю бизнес-логику и правила валидации для элементов.
    
    Атрибуты:
        id: Уникальный идентификатор элемента (None для новых элементов)
        name: Название элемента (обязательное)
        description: Описание элемента (необязательное)
        price: Цена элемента (должна быть неотрицательной)
        in_stock: Флаг доступности на складе
    """
    
    # Поля сущности с полной типизацией
    id: Optional[int]
    name: str
    description: Optional[str]
    price: Decimal
    in_stock: bool
    
    # Константы для валидации
    MAX_NAME_LENGTH: int = 100
    MAX_DESCRIPTION_LENGTH: int = 500
    MAX_PRICE: Decimal = Decimal("999999.99")
    MIN_PRICE: Decimal = Decimal("0")
    
    def __post_init__(self) -> None:
        """Валидация бизнес-правил после инициализации."""
        self._validate_name()
        self._validate_price()
        if self.description is not None:
            self._validate_description(self.description)
    
    def _validate_name(self) -> None:
        """
        Валидация названия элемента согласно бизнес-правилам.
        
        Исключения:
            ValueError: При некорректном названии
        """
        if not self.name or not self.name.strip():
            raise ValueError("Название элемента не может быть пустым")
        if len(self.name.strip()) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Название элемента не может превышать {self.MAX_NAME_LENGTH} символов"
            )
    
    def _validate_price(self) -> None:
        """
        Валидация цены элемента согласно бизнес-правилам.
        
        Исключения:
            ValueError: При некорректной цене
        """
        if self.price < self.MIN_PRICE:
            raise ValueError("Цена элемента не может быть отрицательной")
        if self.price > self.MAX_PRICE:
            raise ValueError(
                f"Цена элемента не может превышать {self.MAX_PRICE}"
            )
    
    def _validate_description(self, description: str) -> None:
        """
        Валидация описания элемента.
        
        Аргументы:
            description: Описание для валидации
            
        Исключения:
            ValueError: При некорректном описании
        """
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Описание элемента не может превышать {self.MAX_DESCRIPTION_LENGTH} символов"
            )
    
    def update_price(self, new_price: Decimal) -> None:
        """
        Обновление цены элемента с валидацией.
        
        Аргументы:
            new_price: Новая цена элемента
            
        Исключения:
            ValueError: При некорректной цене
        """
        if new_price < self.MIN_PRICE:
            raise ValueError("Цена элемента не может быть отрицательной")
        if new_price > self.MAX_PRICE:
            raise ValueError(
                f"Цена элемента не может превышать {self.MAX_PRICE}"
            )
        self.price = new_price
    
    def set_out_of_stock(self) -> None:
        """Отметить элемент как отсутствующий на складе."""
        self.in_stock = False
    
    def set_in_stock(self) -> None:
        """Отметить элемент как доступный на складе."""
        self.in_stock = True
    
    def update_description(self, new_description: Optional[str]) -> None:
        """
        Обновление описания элемента.
        
        Аргументы:
            new_description: Новое описание элемента или None
            
        Исключения:
            ValueError: При некорректном описании
        """
        if new_description is not None:
            self._validate_description(new_description)
        self.description = new_description
    
    def matches_search_query(self, query: str) -> bool:
        """
        Проверка соответствия элемента поисковому запросу.
        
        Аргументы:
            query: Поисковый запрос
            
        Возвращает:
            True если элемент соответствует запросу, иначе False
        """
        if not query:
            return True
        
        query_lower: str = query.lower().strip()
        name_match: bool = query_lower in self.name.lower()
        description_match: bool = (
            self.description is not None and 
            query_lower in self.description.lower()
        )
        return name_match or description_match
    
    def __str__(self) -> str:
        """Строковое представление элемента."""
        stock_status = "в наличии" if self.in_stock else "нет в наличии"
        return f"Item(id={self.id}, name='{self.name}', price={self.price}, {stock_status})"
    
    def __repr__(self) -> str:
        """Полное представление элемента для отладки."""
        return (
            f"Item("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"price={self.price!r}, "
            f"in_stock={self.in_stock!r}"
            f")"
        )