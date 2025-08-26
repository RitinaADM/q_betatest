"""
Logging configuration and infrastructure for the FastAPI application.
Provides structured logging with proper formatting and log levels.
"""

import logging
import logging.config
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'operation'):
            log_entry["operation"] = record.operation
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in (
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                'relativeCreated', 'thread', 'threadName', 'processName',
                'process', 'message', 'exc_info', 'exc_text', 'stack_info'
            ) and not key.startswith('_'):
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the log message
        formatted = (
            f"{color}[{timestamp}] {record.levelname:8s}{reset} "
            f"{record.name} - {record.getMessage()}"
        )
        
        # Add request context if available
        context_parts = []
        if hasattr(record, 'request_id'):
            context_parts.append(f"req_id={record.request_id}")
        if hasattr(record, 'operation'):
            context_parts.append(f"op={record.operation}")
        
        if context_parts:
            formatted += f" [{', '.join(context_parts)}]"
        
        # Add exception info if present
        if record.exc_info:
            formatted += "\\n" + self.formatException(record.exc_info)
        
        return formatted


class LoggingConfig:
    """Logging configuration manager."""
    
    def __init__(self, app_name: str = "fastapi-app", log_level: str = "INFO"):
        self.app_name = app_name
        self.log_level = log_level.upper()
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def setup_logging(self, use_json_format: bool = False) -> None:
        """Set up logging configuration."""
        # Simple configuration for now
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured for {self.app_name}")


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context to logs."""
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process the logging call, adding context from extra."""
        # Merge extra context
        if 'extra' in kwargs:
            kwargs['extra'].update(self.extra)
        else:
            kwargs['extra'] = self.extra.copy()
        
        return msg, kwargs
    
    def with_context(self, **context) -> 'LoggerAdapter':
        """Create a new adapter with additional context."""
        new_extra = self.extra.copy()
        new_extra.update(context)
        return LoggerAdapter(self.logger, new_extra)


def get_logger(name: str, **context) -> LoggerAdapter:
    """Get a logger with optional context."""
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, context)


# Convenience functions for common logging patterns
def log_operation_start(logger: LoggerAdapter, operation: str, **context) -> None:
    """Log the start of an operation."""
    logger.info(
        f"Starting operation: {operation}",
        extra={"operation": operation, "operation_phase": "start", **context}
    )


def log_operation_success(logger: LoggerAdapter, operation: str, **context) -> None:
    """Log successful completion of an operation."""
    logger.info(
        f"Operation completed successfully: {operation}",
        extra={"operation": operation, "operation_phase": "success", **context}
    )


def log_operation_error(logger: LoggerAdapter, operation: str, error: Exception, **context) -> None:
    """Log operation failure."""
    logger.error(
        f"Operation failed: {operation} - {str(error)}",
        exc_info=True,
        extra={
            "operation": operation,
            "operation_phase": "error",
            "error_type": type(error).__name__,
            **context
        }
    )


# Initialize logging configuration
logging_config = LoggingConfig()

# Export commonly used items
__all__ = [
    'LoggingConfig',
    'LoggerAdapter',
    'get_logger',
    'log_operation_start',
    'log_operation_success',
    'log_operation_error',
    'logging_config'
]