"""Domain-specific exceptions for the Item management system."""

from typing import Dict, Any, Optional
from enum import Enum


class ErrorCode(Enum):
    """Enumeration of error codes for consistent error handling."""
    
    # Item-related errors
    ITEM_NOT_FOUND = "ITEM_NOT_FOUND"
    ITEM_INVALID_DATA = "ITEM_INVALID_DATA"
    ITEM_DUPLICATE = "ITEM_DUPLICATE"
    ITEM_INVALID_PRICE = "ITEM_INVALID_PRICE"
    ITEM_INVALID_NAME = "ITEM_INVALID_NAME"
    ITEM_INVALID_DESCRIPTION = "ITEM_INVALID_DESCRIPTION"
    
    # Repository-related errors
    REPOSITORY_ERROR = "REPOSITORY_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"
    
    # Application-related errors
    INVALID_OPERATION = "INVALID_OPERATION"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # System errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class DomainException(Exception):
    """Base class for all domain exceptions with structured error information."""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode, 
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "context": self.context
            }
        }
        
        if self.cause:
            result["error"]["caused_by"] = str(self.cause)
        
        return result
    
    def __str__(self) -> str:
        """String representation of the exception."""
        return f"[{self.error_code.value}] {self.message}"


class ItemNotFoundError(DomainException):
    """Raised when an item is not found."""
    
    def __init__(self, item_id: int, context: Optional[Dict[str, Any]] = None):
        self.item_id = item_id
        message = f"Item with ID {item_id} not found"
        
        error_context = {"item_id": item_id}
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ITEM_NOT_FOUND,
            context=error_context
        )


class InvalidItemDataError(DomainException):
    """Raised when item data is invalid."""
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None, 
        value: Any = None,
        validation_errors: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.field = field
        self.value = value
        self.validation_errors = validation_errors or {}
        
        error_context = {}
        if field:
            error_context["field"] = field
        if value is not None:
            error_context["invalid_value"] = value
        if self.validation_errors:
            error_context["validation_errors"] = self.validation_errors
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ITEM_INVALID_DATA,
            context=error_context
        )


class DuplicateItemError(DomainException):
    """Raised when trying to create an item that already exists."""
    
    def __init__(self, item_name: str, existing_item_id: Optional[int] = None):
        self.item_name = item_name
        self.existing_item_id = existing_item_id
        
        message = f"Item with name '{item_name}' already exists"
        context = {"item_name": item_name}
        
        if existing_item_id:
            context["existing_item_id"] = existing_item_id
            message += f" (ID: {existing_item_id})"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ITEM_DUPLICATE,
            context=context
        )


class InvalidItemPriceError(InvalidItemDataError):
    """Raised when item price is invalid."""
    
    def __init__(self, price: float, min_price: float = 0.0):
        self.price = price
        self.min_price = min_price
        
        message = f"Invalid item price: {price}. Price must be >= {min_price}"
        
        super().__init__(
            message=message,
            field="price",
            value=price,
            context={
                "min_price": min_price,
                "provided_price": price
            }
        )
        
        # Override error code for specific price error
        self.error_code = ErrorCode.ITEM_INVALID_PRICE


class InvalidItemNameError(InvalidItemDataError):
    """Raised when item name is invalid."""
    
    def __init__(self, name: str, reason: str = "Name cannot be empty"):
        self.name = name
        self.reason = reason
        
        message = f"Invalid item name: '{name}'. {reason}"
        
        super().__init__(
            message=message,
            field="name",
            value=name,
            context={
                "provided_name": name,
                "validation_reason": reason
            }
        )
        
        # Override error code for specific name error
        self.error_code = ErrorCode.ITEM_INVALID_NAME


class RepositoryError(DomainException):
    """Raised when repository operations fail."""
    
    def __init__(self, message: str, operation: str, cause: Optional[Exception] = None):
        self.operation = operation
        
        context = {"operation": operation}
        
        super().__init__(
            message=message,
            error_code=ErrorCode.REPOSITORY_ERROR,
            context=context,
            cause=cause
        )


class DatabaseConnectionError(RepositoryError):
    """Raised when database connection fails."""
    
    def __init__(self, database_url: str, cause: Optional[Exception] = None):
        self.database_url = database_url
        
        message = f"Failed to connect to database: {database_url}"
        
        super().__init__(
            message=message,
            operation="database_connection",
            cause=cause
        )
        
        # Override error code for specific database connection error
        self.error_code = ErrorCode.DATABASE_CONNECTION_ERROR
        self.context["database_url"] = database_url


class DatabaseConstraintError(RepositoryError):
    """Raised when database constraint violations occur."""
    
    def __init__(self, constraint: str, table: str, cause: Optional[Exception] = None):
        self.constraint = constraint
        self.table = table
        
        message = f"Database constraint violation: {constraint} on table {table}"
        
        super().__init__(
            message=message,
            operation="database_constraint_check",
            cause=cause
        )
        
        # Override error code for specific constraint error
        self.error_code = ErrorCode.DATABASE_CONSTRAINT_ERROR
        self.context.update({
            "constraint": constraint,
            "table": table
        })