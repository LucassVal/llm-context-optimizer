#!/usr/bin/env python3
"""
ManifestStore - High-performance manifest storage using diskcache + msgspec.

Stores and indexes manifests for fast querying by tags, entities, type, etc.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Union
from collections import defaultdict
from datetime import datetime

import msgspec
from diskcache import Cache

logger = logging.getLogger(__name__)

# Msgspec encoder/decoder
encoder = msgspec.msgpack.Encoder()
decoder = msgspec.msgpack.Decoder()


class ManifestStore:
    """
    High-performance manifest storage with indexing.

    Features:
    - Persistent storage of manifests with msgspec serialization
    - Inverted indexes for tags, entities, type, status
    - Fast querying with multiple criteria
    - LRU cache eviction
    - Atomic operations
    """

    # Key prefixes
    KEY_PREFIX = "manifest"
    KEY_MANIFEST = f"{KEY_PREFIX}:data:"  # manifest:data:{id}
    KEY_INDEX_TAG = f"{KEY_PREFIX}:index:tag:"  # manifest:index:tag:{tag}
    KEY_INDEX_ENTITY = f"{KEY_PREFIX}:index:entity:"  # manifest:index:entity:{entity}
    KEY_INDEX_TYPE = f"{KEY_PREFIX}:index:type:"  # manifest:index:type:{type}
    KEY_INDEX_STATUS = f"{KEY_PREFIX}:index:status:"  # manifest:index:status:{status}
    KEY_METADATA = f"{KEY_PREFIX}:metadata"
    KEY_ALL_IDS = f"{KEY_PREFIX}:all_ids"

    def __init__(self, cache_path: Optional[Path] = None, size_limit_gb: int = 1):
        """
        Initialize ManifestStore.

        Args:
            cache_path: Path to diskcache directory. If None, uses default location.
            size_limit_gb: Maximum cache size in gigabytes (default 1GB).
        """
        if cache_path is None:
            # Default location: project_root/.neocortex/cache/manifests
            from ..config import get_config

            config = get_config()
            cache_path = config.project_root / ".neocortex" / "cache" / "manifests"

        cache_path.mkdir(parents=True, exist_ok=True)

        # Initialize diskcache
        size_limit_bytes = size_limit_gb * 1024 * 1024 * 1024
        self.cache = Cache(
            directory=str(cache_path),
            size_limit=size_limit_bytes,
            eviction_policy="least-recently-used",
        )

        # In-memory caches
        self._mem_cache = {}
        self._index_cache = {}

        logger.info(f"ManifestStore initialized at {cache_path}")
        logger.info(f"Cache size limit: {size_limit_gb}GB")

    def save_manifest(self, manifest_id: str, manifest: Dict[str, Any]) -> bool:
        """
        Save a manifest and update indexes.

        Args:
            manifest_id: Unique identifier for the manifest
            manifest: Manifest data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate required fields
            if "id" not in manifest:
                manifest["id"] = manifest_id
            if manifest["id"] != manifest_id:
                logger.warning(
                    f"Manifest ID mismatch: {manifest['id']} != {manifest_id}"
                )
                manifest["id"] = manifest_id

            # Ensure timestamps
            current_time = datetime.now().isoformat()
            if "created_at" not in manifest:
                manifest["created_at"] = current_time
            manifest["last_accessed"] = current_time
            manifest["last_modified"] = current_time

            # Ensure lists exist
            for field in ["tags", "entities", "dependencies"]:
                if field not in manifest or not isinstance(manifest[field], list):
                    manifest[field] = []

            # Ensure metadata exists
            if "metadata" not in manifest or not isinstance(manifest["metadata"], dict):
                manifest["metadata"] = {}

            # Save manifest data
            key = f"{self.KEY_MANIFEST}{manifest_id}"
            encoded = encoder.encode(manifest)
            self.cache.set(key, encoded)

            # Update in-memory cache
            self._mem_cache[key] = manifest

            # Update indexes
            self._update_indexes(manifest_id, manifest)

            # Update all IDs list
            self._update_all_ids(manifest_id)

            logger.debug(f"Manifest saved: {manifest_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save manifest {manifest_id}: {e}")
            return False

    def get_manifest(self, manifest_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a manifest by ID.

        Args:
            manifest_id: Manifest identifier

        Returns:
            Manifest data or None if not found
        """
        key = f"{self.KEY_MANIFEST}{manifest_id}"

        # Check memory cache
        if key in self._mem_cache:
            logger.debug(f"Manifest cache hit (memory): {manifest_id}")
            return self._mem_cache[key]

        # Check disk cache
        encoded = self.cache.get(key)
        if encoded:
            try:
                manifest = decoder.decode(encoded)
                # Update memory cache
                self._mem_cache[key] = manifest
                logger.debug(f"Manifest cache hit (disk): {manifest_id}")

                # Update last_accessed timestamp
                manifest["last_accessed"] = datetime.now().isoformat()
                self.save_manifest(manifest_id, manifest)

                return manifest
            except Exception as e:
                logger.warning(f"Failed to decode manifest {manifest_id}: {e}")

        logger.debug(f"Manifest not found: {manifest_id}")
        return None

    def delete_manifest(self, manifest_id: str) -> bool:
        """
        Delete a manifest and remove from indexes.

        Args:
            manifest_id: Manifest identifier

        Returns:
            True if deleted, False otherwise
        """
        try:
            # Get manifest to remove from indexes
            manifest = self.get_manifest(manifest_id)
            if manifest:
                self._remove_from_indexes(manifest_id, manifest)

            # Delete manifest data
            key = f"{self.KEY_MANIFEST}{manifest_id}"
            self.cache.delete(key)

            # Remove from memory cache
            self._mem_cache.pop(key, None)

            # Remove from all IDs
            self._remove_from_all_ids(manifest_id)

            logger.debug(f"Manifest deleted: {manifest_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete manifest {manifest_id}: {e}")
            return False

    def query_manifests(
        self,
        tags: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        manifest_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query manifests by multiple criteria.

        Args:
            tags: Filter by tags (AND logic)
            entities: Filter by entities (AND logic)
            manifest_type: Filter by type ("cortex" or "lobe")
            status: Filter by status ("active", "archived", etc.)
            limit: Maximum results to return
            offset: Offset for pagination

        Returns:
            List of matching manifests
        """
        try:
            # Start with all IDs or apply filters
            candidate_ids = None

            # Apply tag filters
            if tags:
                for tag in tags:
                    tag_ids = self._get_indexed_ids(self.KEY_INDEX_TAG, tag)
                    if candidate_ids is None:
                        candidate_ids = set(tag_ids)
                    else:
                        candidate_ids.intersection_update(tag_ids)

                    if not candidate_ids:
                        return []  # No matches

            # Apply entity filters
            if entities:
                for entity in entities:
                    entity_ids = self._get_indexed_ids(self.KEY_INDEX_ENTITY, entity)
                    if candidate_ids is None:
                        candidate_ids = set(entity_ids)
                    else:
                        candidate_ids.intersection_update(entity_ids)

                    if not candidate_ids:
                        return []  # No matches

            # Apply type filter
            if manifest_type:
                type_ids = self._get_indexed_ids(self.KEY_INDEX_TYPE, manifest_type)
                if candidate_ids is None:
                    candidate_ids = set(type_ids)
                else:
                    candidate_ids.intersection_update(type_ids)

                if not candidate_ids:
                    return []

            # Apply status filter
            if status:
                status_ids = self._get_indexed_ids(self.KEY_INDEX_STATUS, status)
                if candidate_ids is None:
                    candidate_ids = set(status_ids)
                else:
                    candidate_ids.intersection_update(status_ids)

                if not candidate_ids:
                    return []

            # If no filters, get all IDs
            if candidate_ids is None:
                candidate_ids = self._get_all_ids()

            # Convert to list and apply pagination
            sorted_ids = sorted(candidate_ids)
            paginated_ids = sorted_ids[offset : offset + limit]

            # Fetch manifests
            results = []
            for manifest_id in paginated_ids:
                manifest = self.get_manifest(manifest_id)
                if manifest:
                    results.append(manifest)

            logger.debug(f"Query returned {len(results)} manifests")
            return results

        except Exception as e:
            logger.error(f"Failed to query manifests: {e}")
            return []

    def list_all_manifests(self) -> List[Dict[str, Any]]:
        """List all manifests."""
        return self.query_manifests(limit=1000)

    def get_manifest_ids_by_tag(self, tag: str) -> List[str]:
        """Get all manifest IDs with a specific tag."""
        return self._get_indexed_ids(self.KEY_INDEX_TAG, tag)

    def get_manifest_ids_by_entity(self, entity: str) -> List[str]:
        """Get all manifest IDs with a specific entity."""
        return self._get_indexed_ids(self.KEY_INDEX_ENTITY, entity)

    def get_manifest_ids_by_type(self, manifest_type: str) -> List[str]:
        """Get all manifest IDs of a specific type."""
        return self._get_indexed_ids(self.KEY_INDEX_TYPE, manifest_type)

    def get_manifest_ids_by_status(self, status: str) -> List[str]:
        """Get all manifest IDs with a specific status."""
        return self._get_indexed_ids(self.KEY_INDEX_STATUS, status)

    def update_manifest_metadata(
        self, manifest_id: str, metadata: Dict[str, Any], merge: bool = True
    ) -> bool:
        """
        Update manifest metadata.

        Args:
            manifest_id: Manifest identifier
            metadata: Metadata dictionary to update
            merge: If True, merge with existing metadata; if False, replace

        Returns:
            True if successful, False otherwise
        """
        manifest = self.get_manifest(manifest_id)
        if not manifest:
            return False

        if merge:
            if "metadata" not in manifest or not isinstance(manifest["metadata"], dict):
                manifest["metadata"] = {}
            manifest["metadata"].update(metadata)
        else:
            manifest["metadata"] = metadata

        manifest["last_modified"] = datetime.now().isoformat()

        return self.save_manifest(manifest_id, manifest)

    def add_tag(self, manifest_id: str, tag: str) -> bool:
        """Add a tag to a manifest."""
        manifest = self.get_manifest(manifest_id)
        if not manifest:
            return False

        if "tags" not in manifest or not isinstance(manifest["tags"], list):
            manifest["tags"] = []

        if tag not in manifest["tags"]:
            manifest["tags"].append(tag)
            manifest["last_modified"] = datetime.now().isoformat()
            return self.save_manifest(manifest_id, manifest)

        return True  # Tag already exists

    def remove_tag(self, manifest_id: str, tag: str) -> bool:
        """Remove a tag from a manifest."""
        manifest = self.get_manifest(manifest_id)
        if not manifest:
            return False

        if "tags" in manifest and isinstance(manifest["tags"], list):
            if tag in manifest["tags"]:
                manifest["tags"].remove(tag)
                manifest["last_modified"] = datetime.now().isoformat()
                return self.save_manifest(manifest_id, manifest)

        return True  # Tag didn't exist

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        all_ids = self._get_all_ids()
        tag_index = self._get_index_stats(self.KEY_INDEX_TAG)
        entity_index = self._get_index_stats(self.KEY_INDEX_ENTITY)
        type_index = self._get_index_stats(self.KEY_INDEX_TYPE)
        status_index = self._get_index_stats(self.KEY_INDEX_STATUS)

        return {
            "total_manifests": len(all_ids),
            "tag_index_size": len(tag_index),
            "entity_index_size": len(entity_index),
            "type_index_size": len(type_index),
            "status_index_size": len(status_index),
            "cache_size": self.cache.volume(),
            "cache_count": len(self.cache),
            "memory_cache_size": len(self._mem_cache),
        }

    def clear_all(self) -> None:
        """Clear all manifests and indexes."""
        self.cache.clear()
        self._mem_cache.clear()
        self._index_cache.clear()
        logger.info("ManifestStore cleared")

    def _update_indexes(self, manifest_id: str, manifest: Dict[str, Any]) -> None:
        """Update all indexes for a manifest."""
        # Index by tags
        tags = manifest.get("tags", [])
        for tag in tags:
            self._add_to_index(self.KEY_INDEX_TAG, tag, manifest_id)

        # Index by entities
        entities = manifest.get("entities", [])
        for entity in entities:
            self._add_to_index(self.KEY_INDEX_ENTITY, entity, manifest_id)

        # Index by type
        manifest_type = manifest.get("type", "")
        if manifest_type:
            self._add_to_index(self.KEY_INDEX_TYPE, manifest_type, manifest_id)

        # Index by status
        status = manifest.get("status", "")
        if status:
            self._add_to_index(self.KEY_INDEX_STATUS, status, manifest_id)

    def _remove_from_indexes(self, manifest_id: str, manifest: Dict[str, Any]) -> None:
        """Remove a manifest from all indexes."""
        # Remove from tag index
        tags = manifest.get("tags", [])
        for tag in tags:
            self._remove_from_index(self.KEY_INDEX_TAG, tag, manifest_id)

        # Remove from entity index
        entities = manifest.get("entities", [])
        for entity in entities:
            self._remove_from_index(self.KEY_INDEX_ENTITY, entity, manifest_id)

        # Remove from type index
        manifest_type = manifest.get("type", "")
        if manifest_type:
            self._remove_from_index(self.KEY_INDEX_TYPE, manifest_type, manifest_id)

        # Remove from status index
        status = manifest.get("status", "")
        if status:
            self._remove_from_index(self.KEY_INDEX_STATUS, status, manifest_id)

    def _add_to_index(self, index_prefix: str, key: str, manifest_id: str) -> None:
        """Add manifest ID to an index."""
        index_key = f"{index_prefix}{key}"

        # Get current IDs
        current_ids = self._get_indexed_ids_raw(index_key)
        if manifest_id not in current_ids:
            current_ids.append(manifest_id)
            encoded = encoder.encode(current_ids)
            self.cache.set(index_key, encoded)

            # Update cache
            self._index_cache[index_key] = current_ids

    def _remove_from_index(self, index_prefix: str, key: str, manifest_id: str) -> None:
        """Remove manifest ID from an index."""
        index_key = f"{index_prefix}{key}"

        # Get current IDs
        current_ids = self._get_indexed_ids_raw(index_key)
        if manifest_id in current_ids:
            current_ids.remove(manifest_id)
            if current_ids:
                encoded = encoder.encode(current_ids)
                self.cache.set(index_key, encoded)
                self._index_cache[index_key] = current_ids
            else:
                # Empty index, delete the key
                self.cache.delete(index_key)
                self._index_cache.pop(index_key, None)

    def _get_indexed_ids(self, index_prefix: str, key: str) -> List[str]:
        """Get indexed IDs for a key."""
        index_key = f"{index_prefix}{key}"

        # Check cache
        if index_key in self._index_cache:
            return self._index_cache[index_key]

        # Get from disk
        ids = self._get_indexed_ids_raw(index_key)
        self._index_cache[index_key] = ids
        return ids

    def _get_indexed_ids_raw(self, index_key: str) -> List[str]:
        """Get indexed IDs from disk without caching."""
        encoded = self.cache.get(index_key)
        if encoded:
            try:
                return decoder.decode(encoded)
            except Exception as e:
                logger.warning(f"Failed to decode index {index_key}: {e}")

        return []

    def _update_all_ids(self, manifest_id: str) -> None:
        """Add manifest ID to the all IDs list."""
        all_ids = self._get_all_ids()
        if manifest_id not in all_ids:
            all_ids.append(manifest_id)
            encoded = encoder.encode(all_ids)
            self.cache.set(self.KEY_ALL_IDS, encoded)

    def _remove_from_all_ids(self, manifest_id: str) -> None:
        """Remove manifest ID from the all IDs list."""
        all_ids = self._get_all_ids()
        if manifest_id in all_ids:
            all_ids.remove(manifest_id)
            encoded = encoder.encode(all_ids)
            self.cache.set(self.KEY_ALL_IDS, encoded)

    def _get_all_ids(self) -> List[str]:
        """Get all manifest IDs."""
        encoded = self.cache.get(self.KEY_ALL_IDS)
        if encoded:
            try:
                return decoder.decode(encoded)
            except Exception as e:
                logger.warning(f"Failed to decode all IDs: {e}")

        return []

    def _get_index_stats(self, index_prefix: str) -> Dict[str, int]:
        """Get statistics for an index."""
        stats = {}
        # Note: This is inefficient for large indexes; for production,
        # consider maintaining separate metadata
        for key in self.cache.iterkeys():
            if isinstance(key, str) and key.startswith(index_prefix):
                index_key = key[len(index_prefix) :]
                ids = self._get_indexed_ids_raw(key)
                stats[index_key] = len(ids)
        return stats

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cache.close()
        except Exception:
            pass


# Factory function
def create_manifest_store(
    cache_path: Optional[Path] = None, size_limit_gb: int = 1
) -> ManifestStore:
    """
    Create a ManifestStore instance.

    Args:
        cache_path: Optional custom cache directory
        size_limit_gb: Cache size limit in gigabytes

    Returns:
        ManifestStore instance
    """
    return ManifestStore(cache_path=cache_path, size_limit_gb=size_limit_gb)


# Integration with existing ManifestService
class ManifestStoreAdapter:
    """
    Adapter to integrate ManifestStore with existing ManifestService.

    This adapter allows the ManifestService to use ManifestStore
    while maintaining compatibility with the existing API.
    """

    def __init__(self, manifest_store: Optional[ManifestStore] = None):
        self.store = manifest_store or create_manifest_store()

    def get_all_manifests(self) -> Dict[str, Dict[str, Any]]:
        """Get all manifests as dictionary (id -> manifest)."""
        manifests = {}
        for manifest in self.store.list_all_manifests():
            manifests[manifest["id"]] = manifest
        return manifests

    def sync_from_ledger(self, ledger: Dict[str, Any]) -> int:
        """
        Sync manifests from ledger to ManifestStore.

        Args:
            ledger: Full ledger dictionary

        Returns:
            Number of manifests synced
        """
        if "memory_cortex" not in ledger:
            return 0

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex.get("manifests", {})

        count = 0
        for manifest_id, manifest in manifests.items():
            if self.store.save_manifest(manifest_id, manifest):
                count += 1

        logger.info(f"Synced {count} manifests from ledger to ManifestStore")
        return count

    def sync_to_ledger(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync manifests from ManifestStore to ledger.

        Args:
            ledger: Ledger dictionary

        Returns:
            Updated ledger
        """
        if "memory_cortex" not in ledger:
            ledger["memory_cortex"] = {}

        memory_cortex = ledger["memory_cortex"]
        all_manifests = self.get_all_manifests()
        memory_cortex["manifests"] = all_manifests
        ledger["memory_cortex"] = memory_cortex

        return ledger


# Test function
def test_manifest_store():
    """Test ManifestStore functionality."""
    import tempfile
    import shutil

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    cache_dir = temp_dir / "cache"

    try:
        store = ManifestStore(cache_path=cache_dir, size_limit_gb=0.1)

        # Create test manifest
        manifest = {
            "id": "test_lobe",
            "type": "lobe",
            "title": "Test Lobe",
            "tags": ["test", "experimental"],
            "entities": ["entity1", "entity2"],
            "status": "active",
            "metadata": {"test": True},
        }

        # Test save
        assert store.save_manifest("test_lobe", manifest)

        # Test retrieve
        retrieved = store.get_manifest("test_lobe")
        assert retrieved is not None
        assert retrieved["id"] == "test_lobe"
        assert "test" in retrieved["tags"]

        # Test query by tag
        results = store.query_manifests(tags=["test"])
        assert len(results) == 1
        assert results[0]["id"] == "test_lobe"

        # Test query by entity
        results = store.query_manifests(entities=["entity1"])
        assert len(results) == 1

        # Test query by type
        results = store.query_manifests(manifest_type="lobe")
        assert len(results) == 1

        # Test update metadata
        assert store.update_manifest_metadata("test_lobe", {"updated": True})
        updated = store.get_manifest("test_lobe")
        assert updated["metadata"]["updated"] == True

        # Test add/remove tag
        assert store.add_tag("test_lobe", "newtag")
        assert store.remove_tag("test_lobe", "newtag")

        # Test delete
        assert store.delete_manifest("test_lobe")
        assert store.get_manifest("test_lobe") is None

        # Test stats
        stats = store.get_stats()
        assert "total_manifests" in stats

        print("✓ ManifestStore tests passed")

    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    test_manifest_store()
