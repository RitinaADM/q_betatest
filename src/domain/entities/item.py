from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class Item:
    """
    Item domain entity representing a business item.
    Contains business logic and validation rules.
    """
    id: Optional[int]
    name: str
    description: Optional[str]
    price: Decimal
    in_stock: bool
    
    def __post_init__(self):
        """Validate business rules after initialization."""
        self._validate_name()
        self._validate_price()
    
    def _validate_name(self) -> None:
        """Validate item name according to business rules."""
        if not self.name or not self.name.strip():
            raise ValueError("Item name cannot be empty")
        if len(self.name.strip()) > 100:
            raise ValueError("Item name cannot exceed 100 characters")
    
    def _validate_price(self) -> None:
        """Validate item price according to business rules."""
        if self.price < 0:
            raise ValueError("Item price cannot be negative")
        if self.price > Decimal("999999.99"):
            raise ValueError("Item price cannot exceed 999999.99")
    
    def update_price(self, new_price: Decimal) -> None:
        """Update item price with validation."""
        if new_price < 0:
            raise ValueError("Item price cannot be negative")
        if new_price > Decimal("999999.99"):
            raise ValueError("Item price cannot exceed 999999.99")
        self.price = new_price
    
    def set_out_of_stock(self) -> None:
        """Mark item as out of stock."""
        self.in_stock = False
    
    def set_in_stock(self) -> None:
        """Mark item as in stock."""
        self.in_stock = True
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Update item description."""
        if new_description and len(new_description) > 500:
            raise ValueError("Item description cannot exceed 500 characters")
        self.description = new_description
    
    def matches_search_query(self, query: str) -> bool:
        """Check if item matches search query."""
        if not query:
            return True
        
        query_lower = query.lower().strip()
        name_match = query_lower in self.name.lower()
        description_match = (
            self.description is not None and 
            query_lower in self.description.lower()
        )
        return name_match or description_match