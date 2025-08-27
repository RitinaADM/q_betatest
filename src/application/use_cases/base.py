"""
Базовый класс для всех use case'ов приложения.
Предоставляет общую структуру и типизацию для бизнес-логики.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict, Optional, Union
from dataclasses import dataclass

# Типы для входных и выходных данных use case'ов
TRequest = TypeVar('TRequest')
TResponse = TypeVar('TResponse')


@dataclass
class UseCaseResult(Generic[TResponse]):
    """
    Результат выполнения use case с метаданными.
    Инкапсулирует данные ответа и дополнительную информацию.
    """
    data: TResponse
    success: bool = True
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def success_result(
        cls, 
        data: TResponse, 
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'UseCaseResult[TResponse]':
        """Создает успешный результат."""
        return cls(data=data, success=True, message=message, metadata=metadata)

    @classmethod
    def failure_result(
        cls, 
        error_data: TResponse, 
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'UseCaseResult[TResponse]':
        """Создает результат с ошибкой."""
        return cls(data=error_data, success=False, message=message, metadata=metadata)


class BaseUseCase(ABC, Generic[TRequest, TResponse]):
    """
    Абстрактный базовый класс для всех use case'ов.
    
    Определяет общий интерфейс и структуру для реализации бизнес-логики.
    Каждый use case должен наследоваться от этого класса и реализовать метод execute.
    
    Generic параметры:
        TRequest: Тип входных данных для use case
        TResponse: Тип выходных данных use case
    """

    @abstractmethod
    async def execute(self, request: TRequest) -> UseCaseResult[TResponse]:
        """
        Основной метод выполнения use case.
        
        Аргументы:
            request: Входные данные для выполнения use case
            
        Возвращает:
            UseCaseResult с результатом выполнения
            
        Исключения:
            Должны обрабатываться внутри реализации и возвращаться как failure_result
        """
        pass

    async def validate_request(self, request: TRequest) -> Optional[str]:
        """
        Валидация входных данных.
        
        Аргументы:
            request: Входные данные для валидации
            
        Возвращает:
            None если валидация прошла успешно, иначе строку с ошибкой
        """
        return None

    async def before_execute(self, request: TRequest) -> None:
        """
        Хук, выполняемый перед основной логикой use case.
        Может использоваться для логирования, аудита и т.д.
        
        Аргументы:
            request: Входные данные use case
        """
        pass

    async def after_execute(
        self, 
        request: TRequest, 
        result: UseCaseResult[TResponse]
    ) -> None:
        """
        Хук, выполняемый после основной логики use case.
        Может использоваться для логирования, очистки ресурсов и т.д.
        
        Аргументы:
            request: Входные данные use case
            result: Результат выполнения use case
        """
        pass

    async def handle_exception(
        self, 
        request: TRequest, 
        exception: Exception
    ) -> UseCaseResult[TResponse]:
        """
        Обработка исключений, возникших в процессе выполнения.
        
        Аргументы:
            request: Входные данные use case
            exception: Возникшее исключение
            
        Возвращает:
            UseCaseResult с информацией об ошибке
        """
        error_message = f"Ошибка выполнения use case: {str(exception)}"
        # Возвращаем None как error_data, поскольку точный тип неизвестен
        return UseCaseResult.failure_result(
            error_data=None,  # type: ignore
            message=error_message,
            metadata={"exception_type": type(exception).__name__}
        )


class SyncBaseUseCase(ABC, Generic[TRequest, TResponse]):
    """
    Синхронная версия базового use case для случаев, 
    когда асинхронность не требуется.
    """

    @abstractmethod
    def execute(self, request: TRequest) -> UseCaseResult[TResponse]:
        """
        Основной метод выполнения синхронного use case.
        
        Аргументы:
            request: Входные данные для выполнения use case
            
        Возвращает:
            UseCaseResult с результатом выполнения
        """
        pass

    def validate_request(self, request: TRequest) -> Optional[str]:
        """Синхронная валидация входных данных."""
        return None

    def before_execute(self, request: TRequest) -> None:
        """Синхронный хук перед выполнением."""
        pass

    def after_execute(
        self, 
        request: TRequest, 
        result: UseCaseResult[TResponse]
    ) -> None:
        """Синхронный хук после выполнения."""
        pass

    def handle_exception(
        self, 
        request: TRequest, 
        exception: Exception
    ) -> UseCaseResult[TResponse]:
        """Синхронная обработка исключений."""
        error_message = f"Ошибка выполнения use case: {str(exception)}"
        return UseCaseResult.failure_result(
            error_data=None,  # type: ignore
            message=error_message,
            metadata={"exception_type": type(exception).__name__}
        )