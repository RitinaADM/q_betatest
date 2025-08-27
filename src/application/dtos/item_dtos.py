"""
Объекты передачи данных (DTO) для работы с элементами.
Определяют контракты для API запросов и ответов с полной типизацией.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Any, Dict, ClassVar
from decimal import Decimal


class ItemCreateDTO(BaseModel):
    """
    DTO для создания нового элемента.
    Содержит все необходимые поля с валидацией для создания элемента в системе.
    """
    
    # Конфигурация модели
    model_config: ClassVar[ConfigDict] = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Название элемента (обязательное поле)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Описание элемента (необязательное поле)"
    )
    price: Decimal = Field(
        ..., 
        ge=0, 
        le=999999.99, 
        description="Цена элемента (должна быть неотрицательной)"
    )
    in_stock: bool = Field(
        True, 
        description="Доступность элемента на складе"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация названия элемента."""
        if not v or not v.strip():
            raise ValueError('Название элемента не может быть пустым')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Валидация описания элемента."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return v


class ItemUpdateDTO(BaseModel):
    """
    DTO для обновления существующего элемента.
    Все поля необязательные, обновляются только переданные значения.
    """
    
    # Конфигурация модели
    model_config: ClassVar[ConfigDict] = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="Новое название элемента"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Новое описание элемента"
    )
    price: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=999999.99, 
        description="Новая цена элемента"
    )
    in_stock: Optional[bool] = Field(
        None, 
        description="Новый статус доступности элемента"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Валидация названия элемента при обновлении."""
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError('Название элемента не может быть пустым')
            return stripped
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Валидация описания элемента при обновлении."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return v


class ItemResponseDTO(BaseModel):
    """
    DTO для ответов с данными элемента.
    Используется для возврата информации о элементе в API ответах.
    """
    
    # Конфигурация модели
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    id: int = Field(
        ..., 
        gt=0,
        description="Уникальный идентификатор элемента"
    )
    name: str = Field(
        ..., 
        min_length=1,
        description="Название элемента"
    )
    description: Optional[str] = Field(
        None, 
        description="Описание элемента"
    )
    price: Decimal = Field(
        ..., 
        ge=0,
        description="Цена элемента"
    )
    in_stock: bool = Field(
        ..., 
        description="Доступность элемента на складе"
    )


class ItemSearchDTO(BaseModel):
    """
    DTO для поисковых запросов по элементам.
    Содержит параметры для поиска элементов в системе.
    """
    
    # Конфигурация модели
    model_config: ClassVar[ConfigDict] = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Поисковый запрос для поиска элементов"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Валидация поискового запроса."""
        stripped = v.strip()
        if not stripped:
            raise ValueError('Поисковый запрос не может быть пустым')
        return stripped


class ItemDeleteResponseDTO(BaseModel):
    """
    DTO для ответов об удалении элемента.
    Содержит информацию о результате операции удаления.
    """
    
    # Конфигурация модели
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    message: str = Field(
        ..., 
        min_length=1,
        description="Сообщение с подтверждением удаления"
    )
    deleted_item_id: int = Field(
        ..., 
        gt=0,
        description="Идентификатор удаленного элемента"
    )
    deleted_item_name: str = Field(
        ..., 
        min_length=1,
        description="Название удаленного элемента"
    )