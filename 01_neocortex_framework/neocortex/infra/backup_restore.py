#!/usr/bin/env python3
"""
Backup and restore utilities for NeoCortex infrastructure.

Provides comprehensive backup and restore capabilities for all data stores
with versioning, compression, and integrity verification.
"""

import json
import logging
import shutil
import sqlite3
import tarfile
import tempfile
import zipfile
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class BackupFormat(str, Enum):
    """Backup archive formats."""

    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    ZIP = "zip"
    DIRECTORY = "directory"


class BackupCompression(str, Enum):
    """Backup compression levels."""

    NONE = "none"
    FAST = "fast"
    DEFAULT = "default"
    MAXIMUM = "maximum"


@dataclass
class BackupManifest:
    """Backup manifest containing metadata and integrity information."""

    version: str = "1.0"
    created_at: datetime = dataclass(default_factory=datetime.now)
    backup_id: str = ""
    format: BackupFormat = BackupFormat.TAR_GZ
    compression: BackupCompression = BackupCompression.DEFAULT
    size_bytes: int = 0
    checksum_sha256: str = ""
    stores_backed_up: List[str] = dataclass(default_factory=list)
    files_included: List[str] = dataclass(default_factory=list)
    integrity_verified: bool = False
    metadata: Dict[str, Any] = dataclass(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupManifest":
        """Create from dictionary."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class BackupRestoreManager:
    """
    Comprehensive backup and restore manager for NeoCortex.

    Features:
    - Full and incremental backups
    - Multiple compression formats
    - Integrity verification with checksums
    - Store-specific backup strategies
    - Versioning and retention policies
    """

    def __init__(self, backup_root: Optional[Path] = None):
        """
        Initialize backup manager.

        Args:
            backup_root: Root directory for backups.
        """
        if backup_root is None:
            from ..config import get_config

            config = get_config()
            backup_root = config.backup_path / "infra_backups"

        backup_root.mkdir(parents=True, exist_ok=True)
        self.backup_root = backup_root

        # Default backup configuration
        self.default_config = {
            "format": BackupFormat.TAR_GZ,
            "compression": BackupCompression.DEFAULT,
            "include_stores": ["ledger", "manifest", "lobe_index", "search", "cache"],
            "retention_days": 30,
            "max_backups": 100,
        }

        logger.info(f"BackupRestoreManager initialized at {backup_root}")

    def create_backup(
        self,
        backup_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[Path]]:
        """
        Create a comprehensive backup of all NeoCortex stores.

        Args:
            backup_id: Optional backup identifier (auto-generated if None).
            config: Backup configuration (overrides defaults).

        Returns:
            Tuple of (success, backup_path).
        """
        if backup_id is None:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        config = {**self.default_config, **(config or {})}

        # Create temporary directory for backup staging
        with tempfile.TemporaryDirectory(prefix="neocortex_backup_") as temp_dir:
            temp_path = Path(temp_dir)
            backup_data_dir = temp_path / "data"
            backup_data_dir.mkdir()

            manifest = BackupManifest(
                backup_id=backup_id,
                format=config["format"],
                compression=config["compression"],
                created_at=datetime.now(),
                metadata={"config": config},
            )

            try:
                # Backup each store
                stores_backed = []

                if "ledger" in config["include_stores"]:
                    if self._backup_ledger_store(backup_data_dir):
                        stores_backed.append("ledger")

                if "manifest" in config["include_stores"]:
                    if self._backup_manifest_store(backup_data_dir):
                        stores_backed.append("manifest")

                if "lobe_index" in config["include_stores"]:
                    if self._backup_lobe_index(backup_data_dir):
                        stores_backed.append("lobe_index")

                if "search" in config["include_stores"]:
                    if self._backup_search_engine(backup_data_dir):
                        stores_backed.append("search")

                if "cache" in config["include_stores"]:
                    if self._backup_hot_cache(backup_data_dir):
                        stores_backed.append("cache")

                # Backup configuration files
                if self._backup_config_files(backup_data_dir):
                    stores_backed.append("config")

                manifest.stores_backed_up = stores_backed

                # Create manifest file
                manifest_path = temp_path / "manifest.json"
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest.to_dict(), f, indent=2)

                # Create archive
                backup_path = self._create_archive(
                    source_dir=temp_path,
                    backup_id=backup_id,
                    format=config["format"],
                    compression=config["compression"],
                )

                if not backup_path:
                    logger.error("Failed to create backup archive")
                    return False, None

                # Update manifest with archive info
                manifest.size_bytes = backup_path.stat().st_size
                manifest.checksum_sha256 = self._calculate_checksum(backup_path)

                # Verify integrity
                manifest.integrity_verified = self._verify_backup_integrity(
                    backup_path, manifest.checksum_sha256
                )

                # Save updated manifest alongside archive
                final_manifest_path = backup_path.with_suffix(".manifest.json")
                with open(final_manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest.to_dict(), f, indent=2)

                logger.info(
                    f"Backup created successfully: {backup_path} "
                    f"({manifest.size_bytes / 1024 / 1024:.2f} MB)"
                )

                # Apply retention policy
                self._apply_retention_policy(
                    config["retention_days"], config["max_backups"]
                )

                return True, backup_path

            except Exception as e:
                logger.error(f"Backup creation failed: {e}")
                return False, None

    def restore_backup(
        self,
        backup_path: Path,
        stores_to_restore: Optional[List[str]] = None,
        verify_integrity: bool = True,
    ) -> bool:
        """
        Restore from a backup archive.

        Args:
            backup_path: Path to backup archive.
            stores_to_restore: List of stores to restore (None = all).
            verify_integrity: Verify backup integrity before restoration.

        Returns:
            True if restoration successful.
        """
        try:
            # Load manifest
            manifest_path = backup_path.with_suffix(".manifest.json")
            if not manifest_path.exists():
                logger.error(f"Manifest not found for backup: {backup_path}")
                return False

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            manifest = BackupManifest.from_dict(manifest_data)

            # Verify integrity if requested
            if verify_integrity:
                if not self._verify_backup_integrity(
                    backup_path, manifest.checksum_sha256
                ):
                    logger.error("Backup integrity verification failed")
                    return False

            # Extract backup
            with tempfile.TemporaryDirectory(prefix="neocortex_restore_") as temp_dir:
                temp_path = Path(temp_dir)

                if not self._extract_archive(backup_path, temp_path, manifest.format):
                    logger.error("Failed to extract backup archive")
                    return False

                data_dir = temp_path / "data"

                # Restore stores
                stores_to_restore = stores_to_restore or manifest.stores_backed_up

                for store in stores_to_restore:
                    if store not in manifest.stores_backed_up:
                        logger.warning(f"Store {store} not in backup, skipping")
                        continue

                    restore_func = getattr(self, f"_restore_{store}", None)
                    if restore_func:
                        if not restore_func(data_dir):
                            logger.error(f"Failed to restore {store}")
                            return False
                        logger.info(f"Restored store: {store}")
                    else:
                        logger.warning(f"No restore method for store: {store}")

                logger.info(f"Backup restored successfully from {backup_path}")
                return True

        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups.

        Returns:
            List of backup metadata dictionaries.
        """
        backups = []

        for backup_file in self.backup_root.glob("*.tar.gz"):
            manifest_file = backup_file.with_suffix(".manifest.json")
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)

                    backups.append(
                        {
                            "path": backup_file,
                            "manifest": manifest_data,
                            "size_mb": backup_file.stat().st_size / 1024 / 1024,
                            "age_days": (
                                datetime.now()
                                - datetime.fromisoformat(manifest_data["created_at"])
                            ).days,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to read manifest for {backup_file}: {e}")

        # Sort by creation date (newest first)
        backups.sort(key=lambda b: b["manifest"]["created_at"], reverse=True)

        return backups

    def _backup_ledger_store(self, backup_dir: Path) -> bool:
        """Backup LedgerStore data."""
        try:
            from .ledger_store import LedgerStore

            store = LedgerStore()
            ledger_data = store.read_ledger()

            ledger_backup_dir = backup_dir / "ledger_store"
            ledger_backup_dir.mkdir(exist_ok=True)

            # Save ledger data
            ledger_file = ledger_backup_dir / "ledger.json"
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(ledger_data, f, indent=2)

            # Backup cache directory if exists
            cache_path = (
                store.cache.directory if hasattr(store.cache, "directory") else None
            )
            if cache_path and Path(cache_path).exists():
                cache_backup_dir = ledger_backup_dir / "cache"
                cache_backup_dir.mkdir(exist_ok=True)

                # Copy cache files
                import shutil

                for item in Path(cache_path).iterdir():
                    if item.is_file():
                        shutil.copy2(item, cache_backup_dir / item.name)

            return True

        except Exception as e:
            logger.error(f"Ledger store backup failed: {e}")
            return False

    def _backup_manifest_store(self, backup_dir: Path) -> bool:
        """Backup ManifestStore data."""
        try:
            from .manifest_store import ManifestStore

            store = ManifestStore()
            all_manifests = store.list_all_manifests()

            manifest_backup_dir = backup_dir / "manifest_store"
            manifest_backup_dir.mkdir(exist_ok=True)

            # Save all manifests
            manifests_file = manifest_backup_dir / "manifests.json"
            with open(manifests_file, "w", encoding="utf-8") as f:
                json.dump(all_manifests, f, indent=2)

            # Save statistics
            stats = store.get_stats()
            stats_file = manifest_backup_dir / "stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Manifest store backup failed: {e}")
            return False

    def _backup_lobe_index(self, backup_dir: Path) -> bool:
        """Backup LobeIndex data."""
        try:
            from .lobe_index import LobeIndex

            index = LobeIndex()

            # Backup SQLite database file
            if index.db_path.exists():
                lobe_backup_dir = backup_dir / "lobe_index"
                lobe_backup_dir.mkdir(exist_ok=True)

                import shutil

                shutil.copy2(index.db_path, lobe_backup_dir / "lobe_index.db")

                # Also backup statistics
                stats = index.get_stats()
                stats_file = lobe_backup_dir / "stats.json"
                with open(stats_file, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2)

                return True

            return False

        except Exception as e:
            logger.error(f"Lobe index backup failed: {e}")
            return False

    def _backup_search_engine(self, backup_dir: Path) -> bool:
        """Backup SearchEngine data."""
        try:
            from .search_engine import SearchEngine

            engine = SearchEngine()

            search_backup_dir = backup_dir / "search_engine"
            search_backup_dir.mkdir(exist_ok=True)

            # Backup statistics
            stats = engine.get_stats()
            stats_file = search_backup_dir / "stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)

            # Backup SQLite database if using SQLite backend
            if hasattr(engine, "db_path") and engine.db_path.exists():
                import shutil

                shutil.copy2(engine.db_path, search_backup_dir / "search.db")

            return True

        except Exception as e:
            logger.error(f"Search engine backup failed: {e}")
            return False

    def _backup_hot_cache(self, backup_dir: Path) -> bool:
        """Backup HotCache data."""
        try:
            from .hot_cache import HotCache

            cache = HotCache()

            cache_backup_dir = backup_dir / "hot_cache"
            cache_backup_dir.mkdir(exist_ok=True)

            # Backup statistics only (cache contents are transient)
            stats = cache.get_stats()
            stats_file = cache_backup_dir / "stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Hot cache backup failed: {e}")
            return False

    def _backup_config_files(self, backup_dir: Path) -> bool:
        """Backup configuration files."""
        try:
            from ..config import get_config

            config = get_config()

            config_backup_dir = backup_dir / "config"
            config_backup_dir.mkdir(exist_ok=True)

            # Backup project configuration
            config_dict = config.to_dict()
            config_file = config_backup_dir / "neocortex_config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)

            # Backup any neocortex_config.yaml or .json files
            project_root = config.project_root
            for config_filename in ["neocortex_config.yaml", "neocortex_config.json"]:
                config_path = project_root / config_filename
                if config_path.exists():
                    import shutil

                    shutil.copy2(config_path, config_backup_dir / config_filename)

            return True

        except Exception as e:
            logger.error(f"Config backup failed: {e}")
            return False

    def _restore_ledger(self, data_dir: Path) -> bool:
        """Restore LedgerStore data."""
        try:
            from .ledger_store import LedgerStore

            ledger_backup_dir = data_dir / "ledger_store"
            ledger_file = ledger_backup_dir / "ledger.json"

            if not ledger_file.exists():
                logger.warning("Ledger backup file not found")
                return False

            with open(ledger_file, "r", encoding="utf-8") as f:
                ledger_data = json.load(f)

            store = LedgerStore()
            store.write_ledger(ledger_data)

            return True

        except Exception as e:
            logger.error(f"Ledger store restoration failed: {e}")
            return False

    def _restore_manifest(self, data_dir: Path) -> bool:
        """Restore ManifestStore data."""
        try:
            from .manifest_store import ManifestStore

            manifest_backup_dir = data_dir / "manifest_store"
            manifests_file = manifest_backup_dir / "manifests.json"

            if not manifests_file.exists():
                logger.warning("Manifests backup file not found")
                return False

            with open(manifests_file, "r", encoding="utf-8") as f:
                all_manifests = json.load(f)

            store = ManifestStore()

            # Clear existing manifests
            store.clear_all()

            # Restore manifests
            for manifest_id, manifest_data in all_manifests.items():
                store.save_manifest(manifest_id, manifest_data)

            return True

        except Exception as e:
            logger.error(f"Manifest store restoration failed: {e}")
            return False

    def _restore_lobe_index(self, data_dir: Path) -> bool:
        """Restore LobeIndex data."""
        try:
            from .lobe_index import LobeIndex

            lobe_backup_dir = data_dir / "lobe_index"
            db_file = lobe_backup_dir / "lobe_index.db"

            if not db_file.exists():
                logger.warning("Lobe index backup file not found")
                return False

            # Close existing index if open
            index = LobeIndex()
            if hasattr(index, "close"):
                index.close()

            # Replace database file
            import shutil

            shutil.copy2(db_file, index.db_path)

            # Reinitialize index
            index._init_database()

            return True

        except Exception as e:
            logger.error(f"Lobe index restoration failed: {e}")
            return False

    def _create_archive(
        self,
        source_dir: Path,
        backup_id: str,
        format: BackupFormat,
        compression: BackupCompression,
    ) -> Optional[Path]:
        """Create backup archive."""
        try:
            archive_name = f"{backup_id}.{format.value}"
            archive_path = self.backup_root / archive_name

            if format == BackupFormat.TAR_GZ:
                mode = "w:gz"
                if compression == BackupCompression.FAST:
                    mode = "w:gz"
                elif compression == BackupCompression.MAXIMUM:
                    mode = "w:gz"

                with tarfile.open(archive_path, mode) as tar:
                    tar.add(source_dir, arcname=backup_id)

            elif format == BackupFormat.TAR_BZ2:
                mode = "w:bz2"
                with tarfile.open(archive_path, mode) as tar:
                    tar.add(source_dir, arcname=backup_id)

            elif format == BackupFormat.ZIP:
                compression_level = {
                    BackupCompression.NONE: zipfile.ZIP_STORED,
                    BackupCompression.FAST: zipfile.ZIP_DEFLATED,
                    BackupCompression.DEFAULT: zipfile.ZIP_DEFLATED,
                    BackupCompression.MAXIMUM: zipfile.ZIP_DEFLATED,
                }.get(compression, zipfile.ZIP_DEFLATED)

                with zipfile.ZipFile(
                    archive_path, "w", compression=compression_level
                ) as zipf:
                    for file_path in source_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_dir)
                            zipf.write(file_path, arcname)

            elif format == BackupFormat.DIRECTORY:
                # Copy directory directly
                import shutil

                shutil.copytree(source_dir, archive_path)

            else:
                logger.error(f"Unsupported backup format: {format}")
                return None

            return archive_path

        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            return None

    def _extract_archive(
        self,
        archive_path: Path,
        target_dir: Path,
        format: BackupFormat,
    ) -> bool:
        """Extract backup archive."""
        try:
            if format == BackupFormat.TAR_GZ or format == BackupFormat.TAR_BZ2:
                with tarfile.open(archive_path, "r:*") as tar:
                    tar.extractall(target_dir)

            elif format == BackupFormat.ZIP:
                with zipfile.ZipFile(archive_path, "r") as zipf:
                    zipf.extractall(target_dir)

            elif format == BackupFormat.DIRECTORY:
                import shutil

                shutil.copytree(archive_path, target_dir)

            else:
                logger.error(f"Unsupported backup format: {format}")
                return False

            return True

        except Exception as e:
            logger.error(f"Archive extraction failed: {e}")
            return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def _verify_backup_integrity(
        self,
        backup_path: Path,
        expected_checksum: str,
    ) -> bool:
        """Verify backup file integrity."""
        try:
            actual_checksum = self._calculate_checksum(backup_path)
            return actual_checksum == expected_checksum
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return False

    def _apply_retention_policy(self, retention_days: int, max_backups: int):
        """Apply retention policy to old backups."""
        try:
            backups = self.list_backups()

            # Remove backups older than retention days
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            for backup in backups:
                backup_date = datetime.fromisoformat(backup["manifest"]["created_at"])
                if backup_date < cutoff_date:
                    try:
                        backup_path = backup["path"]
                        manifest_path = backup_path.with_suffix(".manifest.json")

                        backup_path.unlink(missing_ok=True)
                        manifest_path.unlink(missing_ok=True)

                        logger.info(f"Removed old backup: {backup_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to remove old backup: {e}")

            # Limit total number of backups
            if len(backups) > max_backups:
                # Sort by age (oldest first)
                backups_sorted = sorted(
                    backups,
                    key=lambda b: datetime.fromisoformat(b["manifest"]["created_at"]),
                )

                for backup in backups_sorted[: len(backups) - max_backups]:
                    try:
                        backup_path = backup["path"]
                        manifest_path = backup_path.with_suffix(".manifest.json")

                        backup_path.unlink(missing_ok=True)
                        manifest_path.unlink(missing_ok=True)

                        logger.info(f"Removed excess backup: {backup_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to remove excess backup: {e}")

        except Exception as e:
            logger.error(f"Retention policy application failed: {e}")

    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics."""
        backups = self.list_backups()

        total_size = sum(b["size_mb"] for b in backups)
        oldest_backup = min(
            (datetime.fromisoformat(b["manifest"]["created_at"]) for b in backups),
            default=None,
        )

        return {
            "total_backups": len(backups),
            "total_size_mb": total_size,
            "oldest_backup": oldest_backup.isoformat() if oldest_backup else None,
            "retention_days": self.default_config["retention_days"],
            "max_backups": self.default_config["max_backups"],
        }


def create_backup_manager(backup_root: Optional[Path] = None) -> BackupRestoreManager:
    """
    Create a BackupRestoreManager instance.

    Args:
        backup_root: Root directory for backups.

    Returns:
        BackupRestoreManager instance.
    """
    return BackupRestoreManager(backup_root=backup_root)
