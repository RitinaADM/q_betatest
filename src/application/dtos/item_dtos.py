from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal


class ItemCreateDTO(BaseModel):
    """Data Transfer Object for creating an item."""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: Decimal = Field(..., ge=0, le=999999.99, description="Item price")
    in_stock: bool = Field(True, description="Whether item is in stock")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ItemUpdateDTO(BaseModel):
    """Data Transfer Object for updating an item."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: Optional[Decimal] = Field(None, ge=0, le=999999.99, description="Item price")
    in_stock: Optional[bool] = Field(None, description="Whether item is in stock")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip() if v else v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ItemResponseDTO(BaseModel):
    """Data Transfer Object for item responses."""
    id: int = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    price: Decimal = Field(..., description="Item price")
    in_stock: bool = Field(..., description="Whether item is in stock")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ItemSearchDTO(BaseModel):
    """Data Transfer Object for item search requests."""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    
    @validator('query')
    def validate_query(cls, v):
        return v.strip()


class ItemDeleteResponseDTO(BaseModel):
    """Data Transfer Object for item deletion responses."""
    message: str = Field(..., description="Deletion confirmation message")
    deleted_item_id: int = Field(..., description="ID of deleted item")
    deleted_item_name: str = Field(..., description="Name of deleted item")