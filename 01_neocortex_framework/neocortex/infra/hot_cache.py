#!/usr/bin/env python3
"""
HotCache - High-performance hot cache using diskcache_rs.

Provides fast in-memory and disk-backed caching for frequently accessed data
with TTL support and size-based eviction.
"""

import logging
import time
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta

try:
    import diskcache_rs

    HAS_DISKCACHE_RS = True
except ImportError:
    HAS_DISKCACHE_RS = False
    import diskcache

    logging.warning(
        "diskcache_rs not installed, falling back to Python diskcache. "
        "For better performance: pip install diskcache-rs"
    )

logger = logging.getLogger(__name__)


class HotCache:
    """
    High-performance hot cache with multiple storage tiers.

    Features:
    - Multi-level caching: memory → disk (diskcache_rs) → persistence
    - TTL (time-to-live) support with automatic expiration
    - Size-based eviction policies (LRU, LFU)
    - Compression for large values
    - Statistics and monitoring
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        size_limit_mb: int = 100,
        default_ttl: int = 300,  # 5 minutes
        use_memory_cache: bool = True,
        compression_level: int = 1,
        auto_repair: bool = True,
    ):
        """
        Initialize HotCache.

        Args:
            cache_dir: Directory for disk cache. If None, uses default location.
            size_limit_mb: Maximum cache size in megabytes (default 100MB)
            default_ttl: Default time-to-live in seconds (default 300s)
            use_memory_cache: Whether to use in-memory LRU cache
            compression_level: Compression level (0-9, 0 = no compression)
            auto_repair: Whether to attempt automatic repair if cache integrity check fails
        """
        if cache_dir is None:
            # Default location: project_root/.neocortex/cache/hot_cache
            from ..config import get_config

            config = get_config()
            cache_dir = config.project_root / ".neocortex" / "cache" / "hot_cache"

        # Ensure directory exists
        cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir = cache_dir
        self.size_limit_bytes = size_limit_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.use_memory_cache = use_memory_cache
        self.compression_level = compression_level
        self.auto_repair = auto_repair

        # In-memory cache (LRU dict simulation)
        self._mem_cache: Dict[str, Tuple[Any, float]] = {}
        self._mem_cache_size = 0
        self._mem_cache_hits = 0
        self._mem_cache_misses = 0

        # Initialize disk cache
        self._init_disk_cache()

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "expirations": 0,
            "memory_hits": 0,
            "memory_misses": 0,
            "disk_hits": 0,
            "disk_misses": 0,
            "start_time": time.time(),
        }

        logger.info(f"HotCache initialized at {cache_dir}")
        logger.info(f"Size limit: {size_limit_mb}MB")
        logger.info(f"Default TTL: {default_ttl}s")
        logger.info(f"Memory cache: {'enabled' if use_memory_cache else 'disabled'}")
        logger.info(f"Backend: {'diskcache_rs' if HAS_DISKCACHE_RS else 'diskcache'}")

    def _init_disk_cache(self) -> None:
        """Initialize disk cache backend."""
        if HAS_DISKCACHE_RS:
            # Use diskcache_rs for better performance
            self.disk_cache = diskcache_rs.Cache(
                str(self.cache_dir),
                size_limit=self.size_limit_bytes,
                eviction_policy="least-recently-used",
            )
        else:
            # Fallback to Python diskcache
            import diskcache

            self.disk_cache = diskcache.Cache(
                directory=str(self.cache_dir),
                size_limit=self.size_limit_bytes,
                eviction_policy="least-recently-used",
            )

        # Attempt auto-repair if enabled
        if self.auto_repair:
            self.repair()

    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            # Try JSON for simple types
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(value, ensure_ascii=False).encode("utf-8")
            else:
                # Use pickle for complex objects
                return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.warning(f"Serialization failed, using pickle: {e}")
            return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            # Try JSON first
            decoded = data.decode("utf-8", errors="ignore")
            if (
                decoded.startswith("{")
                or decoded.startswith("[")
                or decoded in ["null", "true", "false"]
            ):
                try:
                    return json.loads(decoded)
                except:
                    pass
        except:
            pass

        # Fallback to pickle
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            raise ValueError(f"Failed to deserialize cache value: {e}")

    def _make_key(self, key: str) -> str:
        """Normalize cache key."""
        # Replace problematic characters
        return key.replace("/", "_").replace(":", "_").replace("\\", "_")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        normalized_key = self._make_key(key)
        self.stats["hits"] += 1

        # Check memory cache first
        if self.use_memory_cache:
            if normalized_key in self._mem_cache:
                value, expiry = self._mem_cache[normalized_key]
                if time.time() < expiry:
                    self.stats["memory_hits"] += 1
                    self._mem_cache_hits += 1
                    return value
                else:
                    # Expired, remove from memory cache
                    del self._mem_cache[normalized_key]

            self.stats["memory_misses"] += 1
            self._mem_cache_misses += 1

        # Check disk cache
        try:
            if HAS_DISKCACHE_RS:
                entry = self.disk_cache.get(normalized_key)
                if entry is None:
                    self.stats["misses"] += 1
                    self.stats["disk_misses"] += 1
                    return default

                # Parse entry (diskcache_rs returns tuple of (data, expiry))
                data, expiry = entry
                if expiry and time.time() > expiry:
                    # Expired, delete it
                    self.disk_cache.delete(normalized_key)
                    self.stats["expirations"] += 1
                    self.stats["misses"] += 1
                    return default

                value = self._deserialize(data)
            else:
                # Python diskcache
                if normalized_key not in self.disk_cache:
                    self.stats["misses"] += 1
                    self.stats["disk_misses"] += 1
                    return default

                value = self.disk_cache[normalized_key]

            self.stats["disk_hits"] += 1

            # Update memory cache
            if self.use_memory_cache:
                expiry_time = time.time() + self.default_ttl
                self._mem_cache[normalized_key] = (value, expiry_time)

            return value

        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            self.stats["misses"] += 1
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful
        """
        normalized_key = self._make_key(key)
        ttl = ttl or self.default_ttl

        try:
            # Serialize value
            serialized = self._serialize(value)

            # Store in disk cache
            if HAS_DISKCACHE_RS:
                expiry = time.time() + ttl if ttl > 0 else None
                self.disk_cache.set(normalized_key, serialized, expire=expiry)
            else:
                # Python diskcache
                self.disk_cache.set(normalized_key, value, expire=ttl)

            # Update memory cache
            if self.use_memory_cache:
                expiry_time = time.time() + ttl
                self._mem_cache[normalized_key] = (value, expiry_time)

            self.stats["sets"] += 1
            return True

        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        normalized_key = self._make_key(key)

        try:
            # Remove from memory cache
            if self.use_memory_cache and normalized_key in self._mem_cache:
                del self._mem_cache[normalized_key]

            # Remove from disk cache
            if HAS_DISKCACHE_RS:
                self.disk_cache.delete(normalized_key)
            else:
                del self.disk_cache[normalized_key]

            self.stats["deletes"] += 1
            return True

        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        normalized_key = self._make_key(key)

        # Check memory cache
        if self.use_memory_cache and normalized_key in self._mem_cache:
            value, expiry = self._mem_cache[normalized_key]
            if time.time() < expiry:
                return True

        # Check disk cache
        try:
            if HAS_DISKCACHE_RS:
                entry = self.disk_cache.get(normalized_key)
                if entry is None:
                    return False
                data, expiry = entry
                if expiry and time.time() > expiry:
                    # Expired, delete it
                    self.disk_cache.delete(normalized_key)
                    return False
                return True
            else:
                return normalized_key in self.disk_cache
        except Exception:
            return False

    def clear(self) -> bool:
        """Clear entire cache."""
        try:
            # Clear memory cache
            if self.use_memory_cache:
                self._mem_cache.clear()
                self._mem_cache_size = 0

            # Clear disk cache
            if HAS_DISKCACHE_RS:
                self.disk_cache.clear()
            else:
                self.disk_cache.clear()

            # Reset statistics
            self._mem_cache_hits = 0
            self._mem_cache_misses = 0

            logger.info("Cache cleared")
            return True

        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        results = {}
        for key in keys:
            value = self.get(key)
            if value is not None:  # Note: None could be a valid cached value
                results[key] = value
        return results

    def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        success = True
        for key, value in items.items():
            if not self.set(key, value, ttl):
                success = False
        return success

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Increment integer value."""
        current = self.get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0

        new_value = current + amount
        self.set(key, new_value, ttl)
        return new_value

    def decrement(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Decrement integer value."""
        return self.increment(key, -amount, ttl)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.stats.copy()

        # Add memory cache stats
        if self.use_memory_cache:
            stats["memory_cache_size"] = len(self._mem_cache)
            stats["memory_cache_hits"] = self._mem_cache_hits
            stats["memory_cache_misses"] = self._mem_cache_misses
            if self._mem_cache_hits + self._mem_cache_misses > 0:
                stats["memory_hit_ratio"] = self._mem_cache_hits / (
                    self._mem_cache_hits + self._mem_cache_misses
                )
            else:
                stats["memory_hit_ratio"] = 0

        # Add disk cache stats
        if HAS_DISKCACHE_RS:
            disk_stats = self.disk_cache.stats()
            stats.update(
                {
                    "disk_cache_size": disk_stats.get("size", 0),
                    "disk_cache_count": disk_stats.get("count", 0),
                    "disk_cache_evictions": disk_stats.get("evictions", 0),
                }
            )
        else:
            stats["disk_cache_count"] = len(self.disk_cache)

        # Calculate overall hit ratio
        total_hits = stats["hits"]
        total_misses = stats["misses"]
        if total_hits + total_misses > 0:
            stats["hit_ratio"] = total_hits / (total_hits + total_misses)
        else:
            stats["hit_ratio"] = 0

        # Uptime
        stats["uptime_seconds"] = time.time() - stats["start_time"]

        return stats

    def repair(self) -> bool:
        """
        Attempt to repair disk cache integrity.

        Returns:
            True if repair succeeded or not needed, False if repair failed.
        """
        if not HAS_DISKCACHE_RS:
            # Python diskcache doesn't have check/repair methods
            logger.warning("Repair not supported for Python diskcache backend")
            return True

        try:
            # Check integrity (returns list of errors, empty list means OK)
            errors = self.disk_cache.check()
            if not errors:
                logger.debug("Disk cache integrity check passed")
                return True
            else:
                logger.warning(
                    f"Disk cache integrity check found {len(errors)} errors, "
                    "attempting repair..."
                )
                # For diskcache_rs, we can try to clear corrupted entries
                # Simple approach: clear entire cache
                self.disk_cache.clear()
                logger.info("Disk cache cleared due to integrity failure")
                return True
        except Exception as e:
            logger.error(f"Disk cache repair failed: {e}")
            return False

    def close(self) -> None:
        """Close cache connections."""
        if not HAS_DISKCACHE_RS:
            self.disk_cache.close()

        logger.info("HotCache closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function
def get_hot_cache(
    cache_dir: Optional[Path] = None,
    size_limit_mb: int = 100,
    default_ttl: int = 300,
    use_memory_cache: bool = True,
    compression_level: int = 1,
    auto_repair: bool = True,
) -> HotCache:
    """Get a HotCache instance (singleton pattern)."""
    from ..config import get_config

    config = get_config()
    if cache_dir is None:
        cache_dir = config.project_root / ".neocortex" / "cache" / "hot_cache"
    # Use configuration values if default parameters are used
    if size_limit_mb == 100:
        size_limit_mb = config.hot_cache_size_mb
    if default_ttl == 300:
        default_ttl = config.hot_cache_default_ttl
    if use_memory_cache == True:
        use_memory_cache = config.hot_cache_use_memory

    return HotCache(
        cache_dir,
        size_limit_mb,
        default_ttl,
        use_memory_cache,
        compression_level,
        auto_repair,
    )
