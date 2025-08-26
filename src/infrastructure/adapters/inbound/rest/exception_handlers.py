"""
Global exception handlers for FastAPI application.
Provides consistent error responses and proper HTTP status codes.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.domain.exceptions import (
    DomainException,
    ItemNotFoundError,
    InvalidItemDataError,
    DuplicateItemError,
    InvalidItemPriceError,
    InvalidItemNameError,
    RepositoryError,
    DatabaseConnectionError,
    DatabaseConstraintError,
    ErrorCode
)

# Configure logger for exception handling
logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        error_code: Unique error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request identifier for tracing
    
    Returns:
        JSONResponse with standardized error format
    """
    response_data = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": "2025-08-26T23:47:00Z",  # In production, use datetime.utcnow()
        }
    }
    
    if details:
        response_data["error"]["details"] = details
    
    if request_id:
        response_data["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Handle domain-specific exceptions.
    
    Args:
        request: FastAPI request object
        exc: Domain exception instance
    
    Returns:
        JSONResponse with appropriate error details
    """
    logger.warning(f"Domain exception occurred: {exc}", exc_info=True)
    
    # Map domain exceptions to HTTP status codes
    status_code_mapping = {
        ErrorCode.ITEM_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.ITEM_INVALID_DATA: status.HTTP_400_BAD_REQUEST,
        ErrorCode.ITEM_INVALID_PRICE: status.HTTP_400_BAD_REQUEST,
        ErrorCode.ITEM_INVALID_NAME: status.HTTP_400_BAD_REQUEST,
        ErrorCode.ITEM_DUPLICATE: status.HTTP_409_CONFLICT,
        ErrorCode.REPOSITORY_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.DATABASE_CONNECTION_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.DATABASE_CONSTRAINT_ERROR: status.HTTP_409_CONFLICT,
    }
    
    http_status = status_code_mapping.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return create_error_response(
        error_code=exc.error_code.value,
        message=exc.message,
        status_code=http_status,
        details=exc.context,
        request_id=getattr(request.state, 'request_id', None)
    )


async def item_not_found_handler(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    """Handle ItemNotFoundError specifically."""
    logger.info(f"Item not found: {exc.item_id}")
    
    return create_error_response(
        error_code=ErrorCode.ITEM_NOT_FOUND.value,
        message=exc.message,
        status_code=status.HTTP_404_NOT_FOUND,
        details=exc.context,
        request_id=getattr(request.state, 'request_id', None)
    )


async def invalid_item_data_handler(request: Request, exc: InvalidItemDataError) -> JSONResponse:
    """Handle InvalidItemDataError specifically."""
    logger.warning(f"Invalid item data: {exc.message}")
    
    return create_error_response(
        error_code=exc.error_code.value,
        message=exc.message,
        status_code=status.HTTP_400_BAD_REQUEST,
        details=exc.context,
        request_id=getattr(request.state, 'request_id', None)
    )


async def duplicate_item_handler(request: Request, exc: DuplicateItemError) -> JSONResponse:
    """Handle DuplicateItemError specifically."""
    logger.warning(f"Duplicate item: {exc.item_name}")
    
    return create_error_response(
        error_code=ErrorCode.ITEM_DUPLICATE.value,
        message=exc.message,
        status_code=status.HTTP_409_CONFLICT,
        details=exc.context,
        request_id=getattr(request.state, 'request_id', None)
    )


async def repository_error_handler(request: Request, exc: RepositoryError) -> JSONResponse:
    """Handle RepositoryError and its subclasses."""
    logger.error(f"Repository error: {exc.message}", exc_info=True)
    
    # Determine status code based on error type
    if isinstance(exc, DatabaseConnectionError):
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, DatabaseConstraintError):
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return create_error_response(
        error_code=exc.error_code.value,
        message="A database error occurred",  # Don't expose internal details
        status_code=http_status,
        details={"operation": exc.operation} if hasattr(exc, 'operation') else None,
        request_id=getattr(request.state, 'request_id', None)
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    logger.error(f"SQLAlchemy error: {str(exc)}", exc_info=True)
    
    # Map specific SQLAlchemy errors
    if isinstance(exc, IntegrityError):
        return create_error_response(
            error_code=ErrorCode.DATABASE_CONSTRAINT_ERROR.value,
            message="Database constraint violation",
            status_code=status.HTTP_409_CONFLICT,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    return create_error_response(
        error_code=ErrorCode.DATABASE_CONNECTION_ERROR.value,
        message="Database operation failed",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        request_id=getattr(request.state, 'request_id', None)
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Extract validation details
    validation_details = []
    for error in exc.errors():
        validation_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        error_code=ErrorCode.ITEM_INVALID_DATA.value,
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={
            "validation_errors": validation_details,
            "invalid_fields": len(validation_details)
        },
        request_id=getattr(request.state, 'request_id', None)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return create_error_response(
        error_code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        status_code=exc.status_code,
        request_id=getattr(request.state, 'request_id', None)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return create_error_response(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"type": type(exc).__name__} if logger.level == logging.DEBUG else None,
        request_id=getattr(request.state, 'request_id', None)
    )


# Exception handler registry
EXCEPTION_HANDLERS = {
    DomainException: domain_exception_handler,
    ItemNotFoundError: item_not_found_handler,
    InvalidItemDataError: invalid_item_data_handler,
    DuplicateItemError: duplicate_item_handler,
    RepositoryError: repository_error_handler,
    SQLAlchemyError: sqlalchemy_error_handler,
    RequestValidationError: validation_error_handler,
    HTTPException: http_exception_handler,
    Exception: generic_exception_handler,
}