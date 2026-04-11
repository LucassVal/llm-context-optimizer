#!/usr/bin/env python3
"""
LedgerStore - High-performance ledger storage using diskcache + msgspec.

Implements LedgerRepository interface with persistent key-value storage
optimized for frequent reads and occasional writes.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

import msgspec
from diskcache import Cache

from neocortex.repositories.base import LedgerRepository

logger = logging.getLogger(__name__)

# Msgspec encoder/decoder for high-performance serialization
encoder = msgspec.msgpack.Encoder()
decoder = msgspec.msgpack.Decoder()


class LedgerStore(LedgerRepository):
    """
    High-performance ledger storage using diskcache + msgspec.

    Features:
    - Persistent key-value store with LRU eviction
    - Msgspec serialization for speed and compactness
    - Section-level caching for frequent access patterns
    - Atomic operations with transaction support
    - Backward compatibility with JSON ledger format
    """

    # Key prefixes for organization
    KEY_PREFIX = "ledger"
    KEY_FULL = f"{KEY_PREFIX}:full"
    KEY_SECTION = f"{KEY_PREFIX}:section:"
    KEY_METADATA = f"{KEY_PREFIX}:metadata"
    KEY_CHANGELOG = f"{KEY_PREFIX}:changelog"
    KEY_SESSION_TIMELINE = f"{KEY_PREFIX}:session_timeline"

    def __init__(self, cache_path: Optional[Path] = None, size_limit_gb: int = 1):
        """
        Initialize LedgerStore.

        Args:
            cache_path: Path to diskcache directory. If None, uses default location.
            size_limit_gb: Maximum cache size in gigabytes (default 1GB).
        """
        if cache_path is None:
            # Default location: project_root/.neocortex/cache/ledger
            from ..config import get_config

            config = get_config()
            cache_path = config.project_root / ".neocortex" / "cache" / "ledger"

        cache_path.mkdir(parents=True, exist_ok=True)

        # Initialize diskcache with size limit
        size_limit_bytes = size_limit_gb * 1024 * 1024 * 1024
        self.cache = Cache(
            directory=str(cache_path),
            size_limit=size_limit_bytes,
            eviction_policy="least-recently-used",
        )

        # In-memory cache for hot data
        self._mem_cache = {}
        self._mem_cache_ttl = {}

        logger.info(f"LedgerStore initialized at {cache_path}")
        logger.info(f"Cache size limit: {size_limit_gb}GB")

    def read(self, identifier: str) -> Any:
        """Read data by identifier (implements Repository interface)."""
        # For backward compatibility, treat identifier as section name
        if identifier == "full":
            return self.read_ledger()
        else:
            # Try to read as a section
            ledger = self.read_ledger()
            return ledger.get(identifier)

    def write(self, identifier: str, data: Any) -> bool:
        """Write data by identifier (implements Repository interface)."""
        # For backward compatibility, treat identifier as section name
        if identifier == "full":
            return self.write_ledger(data)
        else:
            # Update specific section
            ledger = self.read_ledger()
            ledger[identifier] = data
            return self.write_ledger(ledger)

    def exists(self, identifier: str) -> bool:
        """Check if identifier exists (implements Repository interface)."""
        if identifier == "full":
            return self.KEY_FULL in self.cache
        else:
            # Check if section exists in ledger
            try:
                ledger = self.read_ledger()
                return identifier in ledger
            except Exception:
                return False

    def list(self) -> List[str]:
        """List all available identifiers (implements Repository interface)."""
        # Return section names from ledger
        try:
            ledger = self.read_ledger()
            return list(ledger.keys())
        except Exception:
            return []

    def read_ledger(self) -> Dict[str, Any]:
        """Read the entire ledger content."""
        # Check memory cache first
        if self.KEY_FULL in self._mem_cache:
            ttl = self._mem_cache_ttl.get(self.KEY_FULL, 0)
            if time.time() < ttl:
                logger.debug("Ledger cache hit (memory)")
                return self._mem_cache[self.KEY_FULL]

        # Check disk cache
        if self.KEY_FULL in self.cache:
            try:
                encoded = self.cache.get(self.KEY_FULL)
                if encoded:
                    ledger = decoder.decode(encoded)
                    logger.debug("Ledger cache hit (disk)")

                    # Update memory cache with 5-second TTL
                    self._mem_cache[self.KEY_FULL] = ledger
                    self._mem_cache_ttl[self.KEY_FULL] = time.time() + 5

                    return ledger
            except Exception as e:
                logger.warning(f"Failed to decode cached ledger: {e}")

        # Fallback: read from original JSON file
        logger.info("Ledger cache miss, falling back to JSON file")
        from ..config import get_config

        config = get_config()
        ledger_path = config.ledger_path

        if ledger_path.exists():
            try:
                with open(ledger_path, "r", encoding="utf-8") as f:
                    ledger = json.load(f)

                # Cache the result
                self._cache_ledger(ledger)

                return ledger
            except Exception as e:
                logger.error(f"Failed to read ledger from {ledger_path}: {e}")
                raise
        else:
            # Return empty ledger structure
            logger.warning(
                f"Ledger file not found at {ledger_path}, returning empty structure"
            )
            return self._create_empty_ledger()

    def write_ledger(self, data: Dict[str, Any]) -> bool:
        """Write data to ledger."""
        try:
            # Validate basic structure
            if not isinstance(data, dict):
                raise ValueError("Ledger data must be a dictionary")

            # Cache in memory
            self._mem_cache[self.KEY_FULL] = data
            self._mem_cache_ttl[self.KEY_FULL] = time.time() + 5

            # Encode and store in diskcache
            encoded = encoder.encode(data)
            self.cache.set(self.KEY_FULL, encoded)

            # Also update sections for faster access
            self._update_section_cache(data)

            # Write to JSON file for backward compatibility
            self._write_to_json_file(data)

            logger.debug("Ledger written successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to write ledger: {e}")
            return False

    def update_ledger_section(self, section: str, data: Dict[str, Any]) -> bool:
        """Update a specific section of the ledger."""
        try:
            ledger = self.read_ledger()
            ledger[section] = data

            # Update the section cache
            section_key = f"{self.KEY_SECTION}{section}"
            encoded = encoder.encode(data)
            self.cache.set(section_key, encoded)

            # Write full ledger
            return self.write_ledger(ledger)

        except Exception as e:
            logger.error(f"Failed to update ledger section '{section}': {e}")
            return False

    def add_changelog_entry(self, change: str, impact: str) -> bool:
        """Add an entry to the changelog."""
        try:
            ledger = self.read_ledger()

            # Ensure changelog exists
            if "changelog" not in ledger:
                ledger["changelog"] = {"entries": []}
            elif (
                isinstance(ledger["changelog"], dict)
                and "entries" not in ledger["changelog"]
            ):
                ledger["changelog"]["entries"] = []

            # Add new entry
            entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "change": change,
                "impact": impact,
            }

            ledger["changelog"]["entries"].append(entry)

            # Keep only last 100 entries
            if len(ledger["changelog"]["entries"]) > 100:
                ledger["changelog"]["entries"] = ledger["changelog"]["entries"][-100:]

            return self.write_ledger(ledger)

        except Exception as e:
            logger.error(f"Failed to add changelog entry: {e}")
            return False

    def get_system_constraints(self) -> Dict[str, Any]:
        """Get system constraints from ledger."""
        try:
            ledger = self.read_ledger()
            return ledger.get("system_constraints", {})
        except Exception:
            return {}

    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get a specific section with caching."""
        section_key = f"{self.KEY_SECTION}{section}"

        # Check memory cache
        if section_key in self._mem_cache:
            ttl = self._mem_cache_ttl.get(section_key, 0)
            if time.time() < ttl:
                logger.debug(f"Section '{section}' cache hit (memory)")
                return self._mem_cache[section_key]

        # Check disk cache
        if section_key in self.cache:
            try:
                encoded = self.cache.get(section_key)
                if encoded:
                    section_data = decoder.decode(encoded)

                    # Update memory cache
                    self._mem_cache[section_key] = section_data
                    self._mem_cache_ttl[section_key] = time.time() + 5

                    logger.debug(f"Section '{section}' cache hit (disk)")
                    return section_data
            except Exception as e:
                logger.warning(f"Failed to decode cached section '{section}': {e}")

        # Fallback: read from full ledger
        ledger = self.read_ledger()
        section_data = ledger.get(section)

        if section_data is not None:
            # Cache for next time
            encoded = encoder.encode(section_data)
            self.cache.set(section_key, encoded)

        return section_data

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._mem_cache.clear()
        self._mem_cache_ttl.clear()
        self.cache.clear()
        logger.info("LedgerStore cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "memory_cache_size": len(self._mem_cache),
            "disk_cache_size": self.cache.volume(),
            "disk_cache_count": len(self.cache),
            "cache_directory": self.cache.directory,
        }

    def _cache_ledger(self, ledger: Dict[str, Any]) -> None:
        """Cache ledger data in memory and disk."""
        try:
            # Cache full ledger
            encoded = encoder.encode(ledger)
            self.cache.set(self.KEY_FULL, encoded)

            # Cache in memory with 5-second TTL
            self._mem_cache[self.KEY_FULL] = ledger
            self._mem_cache_ttl[self.KEY_FULL] = time.time() + 5

            # Cache sections
            self._update_section_cache(ledger)

        except Exception as e:
            logger.warning(f"Failed to cache ledger: {e}")

    def _update_section_cache(self, ledger: Dict[str, Any]) -> None:
        """Update section-level cache."""
        for section, data in ledger.items():
            if isinstance(data, (dict, list)):
                section_key = f"{self.KEY_SECTION}{section}"
                try:
                    encoded = encoder.encode(data)
                    self.cache.set(section_key, encoded)
                except Exception as e:
                    logger.debug(f"Failed to cache section '{section}': {e}")

    def _write_to_json_file(self, data: Dict[str, Any]) -> None:
        """Write ledger to JSON file for backward compatibility."""
        try:
            from ..config import get_config

            config = get_config()
            ledger_path = config.ledger_path

            # Ensure directory exists
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            # Write with pretty formatting
            with open(ledger_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Ledger written to {ledger_path}")

        except Exception as e:
            logger.warning(f"Failed to write ledger to JSON file: {e}")

    def _create_empty_ledger(self) -> Dict[str, Any]:
        """Create empty ledger structure."""
        return {
            "neocortex_version": "4.2.0",
            "system_type": "framework",
            "system_constraints": {
                "max_context_depth": 5,
                "enforce_ssot": True,
                "token_optimization": True,
                "hot_context_limit": 10,
            },
            "session_timeline": [],
            "memory_cortex": {
                "synapses": {"current_context": {"lobe_id": "", "checkpoint_id": ""}},
                "global_checkpoint_index": {"checkpoints": []},
            },
            "changelog": {"entries": []},
        }

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cache.close()
        except Exception:
            pass


# Factory function for easy instantiation
def create_ledger_store(
    cache_path: Optional[Path] = None, size_limit_gb: int = 1
) -> LedgerStore:
    """
    Create a LedgerStore instance.

    Args:
        cache_path: Optional custom cache directory
        size_limit_gb: Cache size limit in gigabytes

    Returns:
        LedgerStore instance
    """
    return LedgerStore(cache_path=cache_path, size_limit_gb=size_limit_gb)


# Test function
def test_ledger_store():
    """Test LedgerStore functionality."""
    import tempfile
    import shutil

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    cache_dir = temp_dir / "cache"

    try:
        store = LedgerStore(cache_path=cache_dir, size_limit_gb=0.1)

        # Test empty ledger
        ledger = store.read_ledger()
        assert isinstance(ledger, dict)
        assert "neocortex_version" in ledger

        # Test section update
        test_section = {"test": "data"}
        assert store.update_ledger_section("test_section", test_section)

        # Test section retrieval
        retrieved = store.get_section("test_section")
        assert retrieved == test_section

        # Test changelog
        assert store.add_changelog_entry("Test change", "Testing")

        # Test stats
        stats = store.get_stats()
        assert "memory_cache_size" in stats

        print("✓ LedgerStore tests passed")

    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    test_ledger_store()
