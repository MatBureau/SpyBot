"""
Cache system for deal deduplication
"""
import time
from collections import deque
from typing import Set, Tuple
import logging

logger = logging.getLogger(__name__)


class DealCache:
    """
    Thread-safe cache to prevent duplicate deal notifications within a time window
    """

    def __init__(self, cache_duration_hours: int = 24):
        """
        Initialize the deal cache

        Args:
            cache_duration_hours: How long to keep deals in cache (default 24h)
        """
        self.cache_duration_seconds = cache_duration_hours * 3600
        self._cache: deque = deque()  # Stores (asin, timestamp) tuples
        self._asin_set: Set[str] = set()  # Fast lookup

    def _clean_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()

        while self._cache and (current_time - self._cache[0][1]) > self.cache_duration_seconds:
            asin, _ = self._cache.popleft()
            self._asin_set.discard(asin)
            logger.debug(f"Removed expired ASIN from cache: {asin}")

    def is_cached(self, asin: str) -> bool:
        """
        Check if an ASIN is already in cache

        Args:
            asin: Amazon Standard Identification Number

        Returns:
            True if ASIN is in cache, False otherwise
        """
        self._clean_expired()
        return asin in self._asin_set

    def add(self, asin: str) -> None:
        """
        Add an ASIN to the cache

        Args:
            asin: Amazon Standard Identification Number
        """
        self._clean_expired()

        if asin not in self._asin_set:
            current_time = time.time()
            self._cache.append((asin, current_time))
            self._asin_set.add(asin)
            logger.debug(f"Added ASIN to cache: {asin}")

    def clear(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
        self._asin_set.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        self._clean_expired()
        return {
            "total_entries": len(self._cache),
            "cache_duration_hours": self.cache_duration_seconds / 3600
        }
