from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from decimal import Decimal
from typing import Optional

from .config import Base


class ItemModel(Base):
    """
    SQLAlchemy model for Item entity.
    Handles database persistence and mapping.
    """
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True, unique=True)  # Added unique constraint
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_domain_entity(self):
        """Convert SQLAlchemy model to domain entity."""
        from ...domain.entities.item import Item
        
        return Item(
            id=self.id,
            name=self.name,
            description=self.description,
            price=Decimal(str(self.price)) if self.price is not None else Decimal('0'),
            in_stock=self.in_stock
        )
    
    @classmethod
    def from_domain_entity(cls, item, item_id: Optional[int] = None):
        """Create SQLAlchemy model from domain entity."""
        return cls(
            id=item_id or item.id,
            name=item.name,
            description=item.description,
            price=float(item.price),
            in_stock=item.in_stock
        )
    
    def update_from_domain_entity(self, item):
        """Update SQLAlchemy model from domain entity."""
        self.name = item.name
        self.description = item.description
        self.price = float(item.price)
        self.in_stock = item.in_stock