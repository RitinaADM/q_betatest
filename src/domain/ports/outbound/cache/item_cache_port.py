"""
Outbound port interface for Item cache operations.
Defines the contract for item caching operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.item import Item


class ItemCachePort(ABC):
    """
    Outbound port interface for item caching operations.
    This interface defines how the domain can cache items
    for performance optimization (outbound adapters).
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Item]:
        """
        Get an item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, item: Item, ttl: Optional[int] = None) -> None:
        """
        Set an item in cache.
        
        Args:
            key: Cache key
            item: Item to cache
            ttl: Time to live in seconds, None for no expiration
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete an item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if key didn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def clear_all(self) -> None:
        """
        Clear all items from cache.
        """
        pass
    
    @abstractmethod
    async def get_multiple(self, keys: List[str]) -> List[Optional[Item]]:
        """
        Get multiple items from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            List of items (None for missing keys)
        """
        pass
    
    @abstractmethod
    async def set_multiple(self, items: dict[str, Item], ttl: Optional[int] = None) -> None:
        """
        Set multiple items in cache.
        
        Args:
            items: Dictionary of key-item pairs
            ttl: Time to live in seconds, None for no expiration
        """
        pass