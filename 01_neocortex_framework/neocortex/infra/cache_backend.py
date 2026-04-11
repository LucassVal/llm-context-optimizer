#!/usr/bin/env python3
"""
Cache Backend - Abstract interface for cache implementations.

Provides a unified interface for different cache backends (DiskCache, Redis, etc.)
with fallback support and configuration-based selection.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Dict, Union

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear entire cache."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class DiskCacheBackend(CacheBackend):
    """DiskCache-based backend using diskcache library."""

    def __init__(self, cache_dir: Optional[Path] = None, size_limit_mb: int = 100):
        """
        Initialize DiskCache backend.

        Args:
            cache_dir: Directory for cache storage. If None, uses default location.
            size_limit_mb: Maximum cache size in megabytes.
        """
        try:
            import diskcache

            self._cache = diskcache.Cache(
                directory=str(cache_dir) if cache_dir else "diskcache",
                size_limit=size_limit_mb * 1024 * 1024,
                eviction_policy="least-recently-used",
            )
            logger.info(f"DiskCache backend initialized at {cache_dir}")
        except ImportError:
            logger.warning("diskcache not installed, using fallback dictionary")
            self._cache = {}
            self._fallback = True

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        if isinstance(self._cache, dict):
            return self._cache.get(key, default)
        try:
            return self._cache.get(key, default)
        except Exception as e:
            logger.warning(f"Failed to get key {key}: {e}")
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if isinstance(self._cache, dict):
            self._cache[key] = value
            return True
        try:
            self._cache.set(key, value, expire=ttl)
            return True
        except Exception as e:
            logger.warning(f"Failed to set key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if isinstance(self._cache, dict):
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        try:
            return self._cache.delete(key)
        except Exception as e:
            logger.warning(f"Failed to delete key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if isinstance(self._cache, dict):
            return key in self._cache
        try:
            return key in self._cache
        except Exception as e:
            logger.warning(f"Failed to check key {key}: {e}")
            return False

    def clear(self) -> bool:
        """Clear entire cache."""
        if isinstance(self._cache, dict):
            self._cache.clear()
            return True
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if isinstance(self._cache, dict):
            return {
                "type": "dict_fallback",
                "size": len(self._cache),
                "keys": list(self._cache.keys()),
            }
        try:
            return {
                "type": "diskcache",
                "size": self._cache.volume(),
                "count": len(self._cache),
                "directory": self._cache.directory,
            }
        except Exception as e:
            logger.warning(f"Failed to get stats: {e}")
            return {"error": str(e)}


class RedisCacheBackend(CacheBackend):
    """Redis-based cache backend (stub)."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize Redis backend stub.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
        """
        self.host = host
        self.port = port
        self.db = db
        self._connected = False
        logger.info(f"Redis backend stub initialized (not connected)")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from Redis stub."""
        logger.debug(f"Redis stub: get {key}")
        return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis stub."""
        logger.debug(f"Redis stub: set {key} with TTL {ttl}")
        return True

    def delete(self, key: str) -> bool:
        """Delete key from Redis stub."""
        logger.debug(f"Redis stub: delete {key}")
        return True

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis stub."""
        logger.debug(f"Redis stub: exists {key}")
        return False

    def clear(self) -> bool:
        """Clear Redis stub."""
        logger.debug("Redis stub: clear")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis stub statistics."""
        return {
            "type": "redis_stub",
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "connected": self._connected,
        }


# Factory function
def create_cache_backend(backend_type: str = "diskcache", **kwargs) -> CacheBackend:
    """
    Create cache backend instance.

    Args:
        backend_type: "diskcache" or "redis"
        **kwargs: Backend-specific arguments

    Returns:
        CacheBackend instance
    """
    if backend_type == "redis":
        return RedisCacheBackend(**kwargs)
    else:
        # Default to diskcache
        return DiskCacheBackend(**kwargs)


# Test function
def test_cache_backend():
    """Test cache backend functionality."""
    import tempfile
    import shutil

    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Test DiskCacheBackend
        backend = DiskCacheBackend(cache_dir=temp_dir, size_limit_mb=10)
        assert backend.set("test", "value")
        assert backend.get("test") == "value"
        assert backend.exists("test")
        assert backend.delete("test")
        assert not backend.exists("test")
        print("✓ DiskCacheBackend tests passed")

        # Test Redis stub
        redis_backend = RedisCacheBackend()
        stats = redis_backend.get_stats()
        assert stats["type"] == "redis_stub"
        print("✓ RedisCacheBackend stub tests passed")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_cache_backend()
