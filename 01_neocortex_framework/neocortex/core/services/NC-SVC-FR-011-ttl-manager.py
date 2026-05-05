"""---
@Module NC-SVC-FR-011-ttl-manager mcp _genealogy:   injected_at: '2026-04-16T00:23:58.93
---
"""


"""
NC-SVC-FR-011-ttl-manager.py
FR-011  TTL Manager: Time-to-live manager with cachetools.TTLCache for granular entity expiration.

Manages TTLs for sessions, tokens, feature flags, heartbeats, and cache entries.
Uses cachetools.TTLCache with peritem TTL, threadsafe singleton, and EventBus integration.
Publishes entity_expired events automatically on expiration.

Restriction: server.py, sub_server.py are @LOCKS.
This module is a standalone service that can be imported by any module.
"""

import importlib.util
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import cachetools

logger = logging.getLogger(__name__)

# TTLs validados pelo Claude Code (no alterar)
TTL_CONSTANTS = {
    "session": 18000,  # 5 horas (SESSION_LEASE_TTL)
    "token_refresh": 300,  # 5 min antes do vencimento
    "feature_flag": 3600,  # 1 hora
    "heartbeat": 60,  # 1 minuto
    "cache_default": 300,  # 5 minutos
}


class TTLCacheWithEvents(cachetools.TTLCache):
    """
    Extended TTLCache that collects expired keys when expire() is called
    and allows registering perkey expiration callbacks.
    """

    def __init__(self, maxsize: int, ttl: Any, timer=None):
        if timer is None:
            timer = time.monotonic
        super().__init__(maxsize, ttl, timer)
        self._expired_keys = []
        self._callbacks: Dict[str, Callable[[str], None]] = {}
        self._lock = threading.RLock()

    def expire(self, time: Optional[float] = None) -> list:
        """
        Remove expired items and return their keys.
        Overridden to collect expired keys before removal.
        """
        with self._lock:
            if time is None:
                time = self.timer()
            # Collect keys that are expired at `time`
            expired = []
            root = self._TTLCache__root  # type: ignore
            curr = root.next
            while curr is not root:
                if curr.expires <= time:
                    expired.append(curr.key)
                curr = curr.next
            # Remove them via parent's expire
            super().expire(time)
            # Store for external processing
            self._expired_keys.extend(expired)
            return expired

    def pop_expired(self) -> list:
        """Return and clear the list of keys that expired since last call."""
        with self._lock:
            keys = self._expired_keys[:]
            self._expired_keys.clear()
            return keys

    def set_callback(self, key: str, callback: Callable[[str], None]) -> None:
        """Register a callback to be invoked when `key` expires."""
        with self._lock:
            self._callbacks[key] = callback

    def remove_callback(self, key: str) -> None:
        """Remove the expiration callback for `key`."""
        with self._lock:
            self._callbacks.pop(key, None)

    def get_callback(self, key: str) -> Optional[Callable[[str], None]]:
        """Get the expiration callback for `key`, if any."""
        with self._lock:
            return self._callbacks.get(key)

    def __delitem__(self, key, cache_delitem=cachetools.Cache.__delitem__):
        """Override to clean up callback on explicit deletion."""
        with self._lock:
            self._callbacks.pop(key, None)
            super().__delitem__(key)


class TTLManager:
    """
    Threadsafe TTL manager backed by cachetools.TTLCache with perentity TTL,
    expiration events, and EventBus integration (R09).
    """

    _instance: Optional["TTLManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "TTLManager":
        """Singleton pattern with thread safety."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.__init__()
            return cls._instance

    def __init__(self, maxsize: int = 10000):
        """
        Initialize the TTL manager.

        Args:
            maxsize: Maximum number of items the cache can hold (default 10000).
        """
        # Ensure __init__ runs only once for the singleton
        if hasattr(self, "_initialized"):
            return
        self._maxsize = maxsize
        # ttl callable returns perkey TTL seconds
        self._ttl_map: Dict[str, float] = {}
        self._cache = TTLCacheWithEvents(
            maxsize=maxsize,
            ttl=self._get_ttl,
            timer=time.monotonic,
        )
        self._stats = {
            "sets": 0,
            "gets": 0,
            "hits": 0,
            "invalidations": 0,
            "expirations": 0,
            "cleanups": 0,
        }
        self._stats_lock = threading.RLock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._initialized = True
        logger.debug(f"TTLManager initialized with maxsize={maxsize}")

    def _get_ttl(self, key: str, value: Any) -> float:
        """Callable used by TTLCache to obtain TTL for a key."""
        return self._ttl_map.get(key, TTL_CONSTANTS["cache_default"])

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Store a value with a specific TTL.

        Args:
            key: Unique identifier for the entity.
            value: Any picklable value.
            ttl_seconds: TTL in seconds. If None, uses default for key's type.
        """
        with self._cache._lock:
            # Determine TTL
            if ttl_seconds is None:
                # Infer entity type from key pattern? Fallback to default.
                ttl_seconds = TTL_CONSTANTS.get(
                    self._infer_type(key), TTL_CONSTANTS["cache_default"]
                )
            self._ttl_map[key] = float(ttl_seconds)
            self._cache[key] = value  # type: ignore
            # Clear any existing callback; can be added via register_callback()
            self._cache.remove_callback(key)

        with self._stats_lock:
            self._stats["sets"] += 1
        logger.debug(f"TTL set: {key} = {repr(value)[:50]} (ttl={ttl_seconds}s)")

    def get(self, key: str) -> Any:
        """
        Retrieve a value by key. Returns None if key does not exist or has expired.

        Args:
            key: Entity identifier.

        Returns:
            The stored value or None.
        """
        with self._stats_lock:
            self._stats["gets"] += 1
        try:
            value = self._cache[key]
            with self._stats_lock:
                self._stats["hits"] += 1
            logger.debug(f"TTL get hit: {key}")
            return value
        except KeyError:
            logger.debug(f"TTL get miss: {key}")
            return None

    def invalidate(self, key: str) -> bool:
        """
        Explicitly remove a key from the cache, preventing expiration event.

        Args:
            key: Entity identifier.

        Returns:
            True if the key existed and was removed, False otherwise.
        """
        with self._cache._lock:
            if key in self._cache:
                del self._cache[key]
                self._ttl_map.pop(key, None)
                with self._stats_lock:
                    self._stats["invalidations"] += 1
                logger.debug(f"TTL invalidated: {key}")
                return True
            return False

    def cleanup(self) -> int:
        """
        Manually trigger expiration of all overdue items and process their events.

        Returns:
            Number of expired items processed.
        """
        with self._cache._lock:
            expired = self._cache.expire()
            count = len(expired)
            for key in expired:
                self._process_expiration(key)
            with self._stats_lock:
                self._stats["expirations"] += count
                self._stats["cleanups"] += 1
            logger.info(f"TTL cleanup processed {count} expired items")
            return count

    def stats(self) -> Dict[str, Any]:
        """
        Return current cache statistics.

        Returns:
            Dictionary with counts of sets, gets, hits, invalidations,
            expirations, cleanups, and current cache size.
        """
        with self._stats_lock:
            stats = self._stats.copy()
        with self._cache._lock:
            stats["size"] = len(self._cache)
            stats["maxsize"] = self._cache.maxsize
            stats["ttl_map_size"] = len(self._ttl_map)
        return stats

    def register_callback(self, key: str, callback: Callable[[str], None]) -> None:
        """
        Register a callback to be invoked when `key` expires.
        The callback receives the expired key as its only argument.
        """
        with self._cache._lock:
            self._cache.set_callback(key, callback)
        logger.debug(f"Callback registered for key: {key}")

    def start(self) -> None:
        """Start the background thread that periodically processes expirations."""
        with self._lock:
            if self._running:
                logger.warning("TTLManager already running")
                return
            self._running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._expiration_loop, daemon=True)
            self._thread.start()
            logger.info("TTLManager background thread started")

    def stop(self) -> None:
        """Stop the background thread gracefully."""
        with self._lock:
            if not self._running:
                logger.warning("TTLManager not running")
                return
            self._running = False
            self._stop_event.set()
            if self._thread:
                self._thread.join(timeout=5.0)
                if self._thread.is_alive():
                    logger.warning("TTLManager thread did not stop gracefully")
            logger.info("TTLManager background thread stopped")

    def _expiration_loop(self) -> None:
        """Background loop that calls cleanup() every second."""
        while self._running:
            self.cleanup()
            # Wait up to 1 second, but can be interrupted by stop_event
            self._stop_event.wait(timeout=1.0)

    def _process_expiration(self, key: str) -> None:
        """
        Process a single expired key: invoke its callback and publish an event.
        """
        logger.info(f"Entity expired: {key}")
        # Invoke perkey callback if registered
        callback = self._cache.get_callback(key)
        if callback:
            try:
                callback(key)
            except Exception as e:
                logger.error(f"Callback error for {key}: {e}", exc_info=True)

        # Publish event via EventBus (R09)
        self._publish_expiration_event(key)

        # Clean up internal mappings
        with self._cache._lock:
            self._ttl_map.pop(key, None)
            self._cache.remove_callback(key)

    def _publish_expiration_event(self, key: str) -> None:
        """
        Publish an entity_expired event via EventBus.
        Uses spec_from_file_location (R09) to import the hyphennamed module.
        """
        try:
            # R09: mdulos com hfen no suportam import_module
            event_bus_path = Path(__file__).parent / "NC-SVC-FR-005-event-bus.py"
            spec = importlib.util.spec_from_file_location(
                "NC_SVC_FR_005_event_bus", event_bus_path
            )
            if spec is None:
                raise FileNotFoundError("EventBus module spec not found")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore

            event = module.NeoCortexEvent(
                event_type="entity_expired",
                payload={
                    "entity_id": key,
                    "expired_at": datetime.now().isoformat(),
                },
                timestamp=datetime.now(),
                source_tool="TTLManager",
            )
            module.get_event_bus().publish(event)
            logger.debug(f"Published entity_expired event for {key}")
        except FileNotFoundError:
            logger.debug("EventBus module not found, skipping event publication")
        except Exception as e:
            logger.error(f"Failed to publish expiration event: {e}", exc_info=True)

    def _infer_type(self, key: str) -> str:
        """
        Infer entity type from key pattern (simple heuristic).
        Override in subclasses for more sophisticated logic.
        """
        if key.startswith("session:"):
            return "session"
        elif key.startswith("token:"):
            return "token_refresh"
        elif key.startswith("feature:"):
            return "feature_flag"
        elif key.startswith("heartbeat:"):
            return "heartbeat"
        else:
            return "cache_default"

    def __del__(self) -> None:
        """Ensure background thread stops on garbage collection."""
        self.stop()


# Singleton instance for global use (threadsafe via __new__)
_ttl_manager_instance: Optional[TTLManager] = None


def get_ttl_manager() -> TTLManager:
    """Get the singleton TTLManager instance."""
    global _ttl_manager_instance
    with TTLManager._lock:
        if _ttl_manager_instance is None:
            _ttl_manager_instance = TTLManager()
        return _ttl_manager_instance
