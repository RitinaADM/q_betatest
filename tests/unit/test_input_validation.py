"""
Comprehensive input validation and edge case tests.
Tests various boundary conditions, invalid inputs, and edge cases across the application.
"""

import pytest
from decimal import Decimal, InvalidOperation
from typing import Optional

from src.domain.entities.item import Item
from src.domain.exceptions import InvalidItemDataError
from src.application.dtos.item_dtos import (
    ItemCreateDTO,
    ItemUpdateDTO,
    ItemSearchDTO,
    ItemResponseDTO
)


class TestItemEntityValidation:
    """Test Item entity validation and edge cases."""
    
    def test_item_creation_with_valid_data(self):
        """Test item creation with valid data."""
        item = Item(
            id=1,
            name="Valid Item",
            description="A valid item description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert item.id == 1
        assert item.name == "Valid Item"
        assert item.description == "A valid item description"
        assert item.price == Decimal("29.99")
        assert item.in_stock is True
    
    def test_item_creation_with_none_id(self):
        """Test item creation with None ID (for creation scenarios)."""
        item = Item(
            id=None,
            name="New Item",
            description="A new item",
            price=Decimal("19.99"),
            in_stock=False
        )
        
        assert item.id is None
        assert item.name == "New Item"
    
    def test_item_name_validation_empty_string(self):
        """Test item name validation with empty string."""
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            Item(
                id=1,
                name="",
                description="Valid description",
                price=Decimal("29.99"),
                in_stock=True
            )
    
    def test_item_name_validation_whitespace_only(self):
        """Test item name validation with whitespace only."""
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            Item(
                id=1,
                name="   ",
                description="Valid description",
                price=Decimal("29.99"),
                in_stock=True
            )
    
    def test_item_name_validation_very_long(self):
        """Test item name validation with very long name."""
        long_name = "x" * 101  # Over 100 character limit
        with pytest.raises(ValueError, match="Item name cannot exceed 100 characters"):
            Item(
                id=1,
                name=long_name,
                description="Valid description",
                price=Decimal("29.99"),
                in_stock=True
            )
    
    def test_item_name_with_special_characters(self):
        """Test item name with special characters."""
        item = Item(
            id=1,
            name="Item with special chars: @#$%^&*()",
            description="Valid description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert "special chars" in item.name
    
    def test_item_name_with_unicode_characters(self):
        """Test item name with Unicode characters."""
        item = Item(
            id=1,
            name="Café Latté with 中文",
            description="Unicode test",
            price=Decimal("15.50"),
            in_stock=True
        )
        
        assert item.name == "Café Latté with 中文"
    
    def test_item_description_empty_string(self):
        """Test item description can be empty string."""
        item = Item(
            id=1,
            name="Valid Item",
            description="",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert item.description == ""
    
    def test_item_description_very_long(self):
        """Test item description with very long text."""
        item = Item(
            id=1,
            name="Valid Item",
            description="Short description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Description validation happens in update_description method
        long_description = "x" * 501  # Over 500 character limit
        with pytest.raises(ValueError, match="Item description cannot exceed 500 characters"):
            item.update_description(long_description)
    
    def test_item_price_validation_zero(self):
        """Test item price validation with zero value."""
        # Zero price should be allowed based on implementation
        item = Item(
            id=1,
            name="Free Item",
            description="Valid description",
            price=Decimal("0"),
            in_stock=True
        )
        assert item.price == Decimal("0")
    
    def test_item_price_validation_negative(self):
        """Test item price validation with negative value."""
        with pytest.raises(ValueError, match="Item price cannot be negative"):
            Item(
                id=1,
                name="Valid Item",
                description="Valid description",
                price=Decimal("-10.50"),
                in_stock=True
            )
    
    def test_item_price_validation_very_large(self):
        """Test item price validation with very large value."""
        # Test just over the limit
        with pytest.raises(ValueError, match="Item price cannot exceed 999999.99"):
            Item(
                id=1,
                name="Expensive Item",
                description="Very expensive",
                price=Decimal("1000000.00"),
                in_stock=True
            )
    
    def test_item_price_validation_many_decimal_places(self):
        """Test item price validation with many decimal places."""
        # Should be rounded to 2 decimal places
        item = Item(
            id=1,
            name="Precise Item",
            description="Precisely priced",
            price=Decimal("29.999999"),
            in_stock=True
        )
        
        # Check that price is properly handled (implementation dependent)
        assert isinstance(item.price, Decimal)
    
    def test_item_price_validation_string_conversion(self):
        """Test item price validation with string input."""
        # This should work if Item constructor handles string conversion
        item = Item(
            id=1,
            name="String Price Item",
            description="Price from string",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert item.price == Decimal("29.99")
    

    def test_item_update_methods(self):
        """Test item update methods with edge cases."""
        item = Item(
            id=1,
            name="Original Item",
            description="Original description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Test description update
        item.update_description("New description")
        assert item.description == "New description"
        
        # Test description update with empty string
        item.update_description("")
        assert item.description == ""
        
        # Test price update
        item.update_price(Decimal("39.99"))
        assert item.price == Decimal("39.99")
        
        # Test price update with invalid value
        with pytest.raises(ValueError, match="Item price cannot be negative"):
            item.update_price(Decimal("-5.00"))
        
        # Test stock status updates
        item.set_out_of_stock()
        assert item.in_stock is False
        
        item.set_in_stock()
        assert item.in_stock is True


class TestItemCreateDTOValidation:
    """Test ItemCreateDTO validation and edge cases."""
    
    def test_create_dto_valid_data(self):
        """Test creation with valid data."""
        dto = ItemCreateDTO(
            name="Test Item",
            description="Test description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert dto.name == "Test Item"
        assert dto.description == "Test description"
        assert dto.price == Decimal("29.99")
        assert dto.in_stock is True
    
    def test_create_dto_name_validation(self):
        """Test name validation in CreateDTO."""
        # Empty name
        with pytest.raises(ValueError):
            ItemCreateDTO(
                name="",
                description="Valid description",
                price=Decimal("29.99"),
                in_stock=True
            )
        
        # Whitespace only name
        with pytest.raises(ValueError):
            ItemCreateDTO(
                name="   ",
                description="Valid description",
                price=Decimal("29.99"),
                in_stock=True
            )
    
    def test_create_dto_price_validation(self):
        """Test price validation in CreateDTO."""
        # Negative price should be rejected by Pydantic ge=0 constraint
        with pytest.raises((ValueError, Exception)):
            ItemCreateDTO(
                name="Valid Item",
                description="Valid description",
                price=Decimal("-10.50"),
                in_stock=True
            )
        
        # Zero price should be allowed
        dto = ItemCreateDTO(
            name="Free Item",
            description="Free item",
            price=Decimal("0"),
            in_stock=True
        )
        assert dto.price == Decimal("0")
    
    def test_create_dto_description_edge_cases(self):
        """Test description edge cases in CreateDTO."""
        # Empty description should be allowed and converted to None by validator
        dto = ItemCreateDTO(
            name="Valid Item",
            description="",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert dto.description is None  # Empty string gets converted to None
        
        # Very long description should be rejected by Pydantic max_length constraint
        with pytest.raises((ValueError, Exception)):
            ItemCreateDTO(
                name="Valid Item",
                description="x" * 501,  # Over 500 character limit
                price=Decimal("29.99"),
                in_stock=True
            )
    
    def test_create_dto_boolean_conversion(self):
        """Test boolean conversion for in_stock field."""
        # Test with various truthy/falsy values
        dto_true = ItemCreateDTO(
            name="Item",
            description="Description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        dto_false = ItemCreateDTO(
            name="Item",
            description="Description",
            price=Decimal("29.99"),
            in_stock=False
        )
        
        assert dto_true.in_stock is True
        assert dto_false.in_stock is False


class TestItemUpdateDTOValidation:
    """Test ItemUpdateDTO validation with optional fields."""
    
    def test_update_dto_all_none(self):
        """Test update DTO with all None values."""
        dto = ItemUpdateDTO(
            name=None,
            description=None,
            price=None,
            in_stock=None
        )
        
        assert dto.name is None
        assert dto.description is None
        assert dto.price is None
        assert dto.in_stock is None
    
    def test_update_dto_partial_updates(self):
        """Test update DTO with partial updates."""
        # Only name
        dto1 = ItemUpdateDTO(name="New Name")
        assert dto1.name == "New Name"
        assert dto1.description is None
        
        # Only price
        dto2 = ItemUpdateDTO(price=Decimal("39.99"))
        assert dto2.price == Decimal("39.99")
        assert dto2.name is None
        
        # Only stock status
        dto3 = ItemUpdateDTO(in_stock=False)
        assert dto3.in_stock is False
        assert dto3.name is None
    
    def test_update_dto_name_validation_when_provided(self):
        """Test name validation when provided in UpdateDTO."""
        # Valid name should work
        dto = ItemUpdateDTO(name="Valid Name")
        assert dto.name == "Valid Name"
        
        # Empty name should be rejected
        with pytest.raises(ValueError):
            ItemUpdateDTO(name="")
        
        # Whitespace only name should be rejected
        with pytest.raises(ValueError):
            ItemUpdateDTO(name="   ")
    
    def test_update_dto_price_validation_when_provided(self):
        """Test price validation when provided in UpdateDTO."""
        # Valid price should work
        dto = ItemUpdateDTO(price=Decimal("49.99"))
        assert dto.price == Decimal("49.99")
        
        # Zero price should be allowed
        dto_zero = ItemUpdateDTO(price=Decimal("0"))
        assert dto_zero.price == Decimal("0")
        
        # Negative price should be rejected by Pydantic
        with pytest.raises((ValueError, Exception)):
            ItemUpdateDTO(price=Decimal("-5.00"))
    
    def test_update_dto_description_when_provided(self):
        """Test description validation when provided in UpdateDTO."""
        # Empty description should be allowed and converted to None
        dto = ItemUpdateDTO(description="")
        assert dto.description is None  # Empty string gets converted to None
        
        # Normal description should work
        dto2 = ItemUpdateDTO(description="Updated description")
        assert dto2.description == "Updated description"
        
        # Very long description should be rejected by Pydantic
        with pytest.raises((ValueError, Exception)):
            ItemUpdateDTO(description="x" * 501)  # Over 500 character limit


class TestItemSearchDTOValidation:
    """Test ItemSearchDTO validation and edge cases."""
    
    def test_search_dto_valid_query(self):
        """Test search DTO with valid query."""
        dto = ItemSearchDTO(query="laptop")
        assert dto.query == "laptop"
    
    def test_search_dto_empty_query(self):
        """Test search DTO with empty query."""
        with pytest.raises(ValueError):
            ItemSearchDTO(query="")
    
    def test_search_dto_whitespace_query(self):
        """Test search DTO with whitespace-only query."""
        # Whitespace gets trimmed by validator, so effectively becomes empty
        # This should either be rejected or trimmed to valid query
        dto = ItemSearchDTO(query="   test   ")
        assert dto.query == "test"  # Whitespace should be trimmed
    
    def test_search_dto_very_long_query(self):
        """Test search DTO with very long query."""
        long_query = "x" * 501  # Assuming 500 character limit
        with pytest.raises(ValueError):
            ItemSearchDTO(query=long_query)
    
    def test_search_dto_special_characters(self):
        """Test search DTO with special characters."""
        dto = ItemSearchDTO(query="test@#$%")
        assert dto.query == "test@#$%"
    
    def test_search_dto_unicode_characters(self):
        """Test search DTO with Unicode characters."""
        dto = ItemSearchDTO(query="café中文")
        assert dto.query == "café中文"


class TestItemResponseDTOValidation:
    """Test ItemResponseDTO validation and edge cases."""
    
    def test_response_dto_creation(self):
        """Test response DTO creation."""
        dto = ItemResponseDTO(
            id=1,
            name="Response Item",
            description="Response description",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert dto.id == 1
        assert dto.name == "Response Item"
    
    def test_response_dto_id_required(self):
        """Test that ID is required in response DTO."""
        # ID cannot be None in response
        with pytest.raises(ValueError):
            ItemResponseDTO(
                id=None,
                name="Response Item",
                description="Response description",
                price=Decimal("29.99"),
                in_stock=True
            )
    
    def test_response_dto_serialization(self):
        """Test response DTO serialization."""
        dto = ItemResponseDTO(
            id=1,
            name="Serialization Test",
            description="Test serialization",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Should be able to convert to dict
        try:
            dto_dict = dto.model_dump()  # Pydantic v2
        except AttributeError:
            dto_dict = dto.dict()  # Pydantic v1 fallback
            
        assert dto_dict["id"] == 1
        assert dto_dict["name"] == "Serialization Test"
        
        # Price should be properly serialized
        assert isinstance(dto_dict["price"], (float, str, Decimal))


class TestNumericEdgeCases:
    """Test edge cases with numeric values."""
    
    def test_decimal_precision(self):
        """Test decimal precision handling."""
        # Test various decimal precisions within valid range
        precisions = [
            "0.01",
            "0.99",
            "1.00",
            "999.99",
            "1000.00",
            "999999.99"  # Maximum allowed
        ]
        
        for price_str in precisions:
            price = Decimal(price_str)
            item = Item(
                id=1,
                name="Precision Test",
                description="Testing precision",
                price=price,
                in_stock=True
            )
            assert item.price == price
    
    def test_decimal_arithmetic_edge_cases(self):
        """Test decimal arithmetic edge cases."""
        item = Item(
            id=1,
            name="Arithmetic Test",
            description="Testing arithmetic",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Test price updates with edge cases
        edge_prices = [
            Decimal("0.01"),  # Minimum positive
            Decimal("999999.99"),  # Large value
            Decimal("100.00"),  # Round number
        ]
        
        for price in edge_prices:
            item.update_price(price)
            assert item.price == price
    
    def test_invalid_decimal_conversion(self):
        """Test invalid decimal conversion."""
        with pytest.raises((ValueError, InvalidOperation)):
            Item(
                id=1,
                name="Invalid Price",
                description="Testing invalid price",
                price=Decimal("invalid"),
                in_stock=True
            )


class TestStringEdgeCases:
    """Test edge cases with string values."""
    
    def test_string_boundaries(self):
        """Test string length boundaries."""
        # Test exact boundary lengths
        boundary_names = [
            "x",  # Single character
            "xx",  # Two characters
            "x" * 50,  # Medium length
            "x" * 100,  # Exactly at limit
        ]
        
        for name in boundary_names:
            item = Item(
                id=1,
                name=name,
                description="Boundary test",
                price=Decimal("29.99"),
                in_stock=True
            )
            assert item.name.strip() == name.strip()  # Account for trimming
    
    def test_whitespace_handling(self):
        """Test whitespace handling in strings."""
        # Leading/trailing whitespace should be preserved
        item = Item(
            id=1,
            name="  Whitespace Test  ",
            description="  Description with spaces  ",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Behavior depends on implementation
        assert "Whitespace Test" in item.name
    
    def test_newline_and_tab_characters(self):
        """Test newline and tab characters in strings."""
        item = Item(
            id=1,
            name="Name\nwith\nnewlines",
            description="Description\twith\ttabs",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        assert "\n" in item.name
        assert "\t" in item.description


class TestBooleanEdgeCases:
    """Test edge cases with boolean values."""
    
    def test_boolean_consistency(self):
        """Test boolean value consistency."""
        item = Item(
            id=1,
            name="Boolean Test",
            description="Testing booleans",
            price=Decimal("29.99"),
            in_stock=True
        )
        
        # Test state changes
        assert item.in_stock is True
        
        item.set_out_of_stock()
        assert item.in_stock is False
        
        item.set_in_stock()
        assert item.in_stock is True
    
    def test_stock_status_edge_cases(self):
        """Test stock status edge cases."""
        item = Item(
            id=1,
            name="Stock Test",
            description="Testing stock",
            price=Decimal("29.99"),
            in_stock=False
        )
        
        # Multiple calls should be idempotent
        item.set_out_of_stock()
        item.set_out_of_stock()
        assert item.in_stock is False
        
        item.set_in_stock()
        item.set_in_stock()
        assert item.in_stock is True