from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class ItemId:
    """Value object for Item ID."""
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Item ID must be positive")


@dataclass(frozen=True)
class ItemName:
    """Value object for Item name with validation."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Item name cannot be empty")
        if len(self.value.strip()) > 100:
            raise ValueError("Item name cannot exceed 100 characters")
    
    @property
    def normalized(self) -> str:
        """Return normalized name for comparisons."""
        return self.value.strip().lower()


@dataclass(frozen=True)
class Price:
    """Value object for price with validation."""
    value: Decimal
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Price cannot be negative")
        if self.value > Decimal("999999.99"):
            raise ValueError("Price cannot exceed 999999.99")
    
    def __str__(self) -> str:
        return f"${self.value:.2f}"


@dataclass(frozen=True)
class ItemDescription:
    """Value object for Item description."""
    value: Optional[str]
    
    def __post_init__(self):
        if self.value and len(self.value) > 500:
            raise ValueError("Item description cannot exceed 500 characters")
    
    @property
    def normalized(self) -> str:
        """Return normalized description for search."""
        return (self.value or "").strip().lower()