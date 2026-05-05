"""---
@Service NC-SVC-FR-004-cache-service mcp _genealogy:   injected_at: '2026-04-16T00:23:58.67
---
"""


"""
NC-SVC-FR-004-cache-service.py
FR-004  HotCache Service: In-memory cache with TTL for NeoCortex.

Provides a singleton in-memory cache with TTL expiration, stats tracking,
and automatic pruning of expired entries.

Restriction: server.py, sub_server.py are @LOCKS.
This module is a standalone service that can be imported by any module.
"""

import logging
import time
from threading import RLock
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HotCache:
    """In-memory cache with TTL and statistics."""

    _instance: Optional["HotCache"] = None
    _lock: RLock
    _cache: dict[str, tuple[Any, float | None]]
    _hits: int
    _misses: int
    _max_size: int
    _default_ttl: int

    def __new__(cls) -> "HotCache":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._lock = RLock()
            cls._instance._cache = {}
            cls._instance._hits = 0
            cls._instance._misses = 0
            cls._instance._max_size = 500
            cls._instance._default_ttl = 300  # 5 minutes
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from get_config()."""
        try:
            from neocortex.config import get_config

            cfg = get_config()
            self._max_size = cfg.get("cache_max_size", 500)
            self._default_ttl = cfg.get("cache_default_ttl", 300)
        except Exception as e:
            logger.warning(f"Failed to load cache config: {e}. Using defaults.")

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """
        Store a value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds. None uses default TTL.
        """
        with self._lock:
            self._prune_expired()
            if len(self._cache) >= self._max_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"Cache full, evicted {oldest_key}")

            expire_at = None
            if ttl is None:
                ttl = self._default_ttl
            if ttl > 0:
                expire_at = time.time() + ttl

            self._cache[key] = (value, expire_at)
            logger.debug(f"Cache set: {key} (ttl={ttl}s)")

    def get(self, key: str) -> Any | None:
        """
        Retrieve a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired.
        """
        with self._lock:
            self._prune_expired()
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"Cache miss: {key}")
                return None

            value, expire_at = self._cache[key]
            if expire_at is not None and expire_at < time.time():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired: {key}")
                return None

            self._hits += 1
            logger.debug(f"Cache hit: {key}")
            return value

    def invalidate(self, key: str) -> bool:
        """
        Remove a key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was removed, False if not found.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache invalidated: {key}")
                return True
            return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries removed.
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info(f"Cache cleared, removed {count} entries")
            return count

    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with size, hits, misses, hit_rate.
        """
        with self._lock:
            self._prune_expired()
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "max_size": self._max_size,
                "default_ttl": self._default_ttl,
            }

    def _prune_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of expired entries removed.
        """
        with self._lock:
            now = time.time()
            expired_keys = [
                key
                for key, (_, expire_at) in self._cache.items()
                if expire_at is not None and expire_at < now
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.debug(f"Pruned {len(expired_keys)} expired cache entries")
            return len(expired_keys)


# Convenience function
def get_hot_cache() -> HotCache:
    """Get the singleton HotCache instance."""
    return HotCache()
