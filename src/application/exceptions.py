"""Application-specific exceptions."""


class ApplicationException(Exception):
    """Base class for all application exceptions."""
    pass


class ValidationError(ApplicationException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)


class ServiceError(ApplicationException):
    """Raised when a service operation fails."""
    pass