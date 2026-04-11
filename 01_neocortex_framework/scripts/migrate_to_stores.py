#!/usr/bin/env python3
"""
Migration script for NeoCortex data stores.

Migrates existing JSON ledger and .mdc files to the new high-performance
stores (LedgerStore, ManifestStore, LobeIndex).
"""

import json
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from neocortex.infra.ledger_store import LedgerStore
from neocortex.infra.manifest_store import ManifestStore
from neocortex.infra.lobe_index import LobeIndex
from neocortex.config import get_config

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manager for data migration to new stores."""

    def __init__(self):
        self.config = get_config()
        self.backup_dir = self.config.backup_path / "migration_backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize stores
        self.ledger_store = LedgerStore()
        self.manifest_store = ManifestStore()
        self.lobe_index = LobeIndex()

        self.stats = {
            "ledger_entries": 0,
            "manifests": 0,
            "lobes": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
        }

    def create_backup(self) -> bool:
        """Create backup of original data."""
        logger.info("Creating backup of original data...")

        backup_files = []

        # Backup ledger JSON
        ledger_path = self.config.ledger_path
        if ledger_path.exists():
            backup_path = (
                self.backup_dir
                / f"ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                import shutil

                shutil.copy2(ledger_path, backup_path)
                backup_files.append(("ledger", str(backup_path)))
                logger.info(f"Backed up ledger to {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup ledger: {e}")
                return False

        # Backup .mdc files from core_central
        mdc_files = list(self.config.core_central.glob("**/*.mdc"))
        if mdc_files:
            mdc_backup_dir = self.backup_dir / "mdc_files"
            mdc_backup_dir.mkdir(exist_ok=True)

            for mdc_file in mdc_files:
                try:
                    relative = mdc_file.relative_to(self.config.core_central)
                    backup_path = mdc_backup_dir / relative
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(mdc_file, backup_path)
                except Exception as e:
                    logger.warning(f"Failed to backup {mdc_file}: {e}")

            backup_files.append(("mdc_files", str(mdc_backup_dir)))
            logger.info(f"Backed up {len(mdc_files)} .mdc files")

        # Save backup manifest
        backup_manifest = {
            "timestamp": datetime.now().isoformat(),
            "backup_files": backup_files,
            "original_paths": {
                "ledger": str(ledger_path),
                "core_central": str(self.config.core_central),
            },
        }

        manifest_path = self.backup_dir / "backup_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(backup_manifest, f, indent=2)

        logger.info(f"Backup completed. Manifest: {manifest_path}")
        return True

    def migrate_ledger(self) -> bool:
        """Migrate JSON ledger to LedgerStore."""
        logger.info("Migrating ledger...")

        ledger_path = self.config.ledger_path
        if not ledger_path.exists():
            logger.warning("Ledger file not found, skipping ledger migration")
            return True

        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger_data = json.load(f)

            logger.info(f"Ledger data type: {type(ledger_data)}")
            logger.info(f"Ledger keys: {list(ledger_data.keys())}")

            # Write to LedgerStore
            self.ledger_store.write_ledger(ledger_data)

            # Verify migration
            stored_data = self.ledger_store.read_ledger()
            if stored_data == ledger_data:
                self.stats["ledger_entries"] = len(ledger_data.get("sections", {}))
                logger.info(f"Migrated {self.stats['ledger_entries']} ledger sections")
                return True
            else:
                logger.error("Ledger verification failed")
                return False

        except Exception as e:
            logger.error(f"Ledger migration failed: {e}")
            logger.error("Traceback: %s", traceback.format_exc())
            return False

    def migrate_manifests(self) -> bool:
        """Migrate .mdc files to ManifestStore."""
        logger.info("Migrating manifests...")

        mdc_files = list(self.config.core_central.glob("**/*.mdc"))
        if not mdc_files:
            logger.warning("No .mdc files found, skipping manifest migration")
            return True

        success_count = 0
        error_count = 0

        for mdc_file in mdc_files:
            try:
                with open(mdc_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse manifest metadata from filename and content
                manifest_id = mdc_file.stem
                relative_path = str(mdc_file.relative_to(self.config.core_central))

                manifest_data = {
                    "id": manifest_id,
                    "path": relative_path,
                    "content": content,
                    "file_type": "mdc",
                    "size_bytes": mdc_file.stat().st_size,
                    "modified_time": mdc_file.stat().st_mtime,
                    "tags": self._extract_tags_from_content(content),
                    "entities": self._extract_entities_from_content(content),
                }

                # Store manifest
                self.manifest_store.save_manifest(manifest_id, manifest_data)
                success_count += 1

            except Exception as e:
                logger.warning(f"Failed to migrate {mdc_file}: {e}")
                error_count += 1

        self.stats["manifests"] = success_count
        if error_count > 0:
            logger.warning(
                f"Migrated {success_count} manifests with {error_count} errors"
            )
        else:
            logger.info(f"Migrated {success_count} manifests successfully")

        return success_count > 0 or error_count == 0

    def migrate_lobes(self) -> bool:
        """Migrate lobe metadata to LobeIndex."""
        logger.info("Migrating lobes...")

        # Scan for lobe directories
        lobes_dir = self.config.core_central / ".agents" / "rules"
        if not lobes_dir.exists():
            logger.warning("Lobes directory not found, skipping lobe migration")
            return True

        lobe_files = list(lobes_dir.glob("*.mdc"))
        success_count = 0
        error_count = 0

        for lobe_file in lobe_files:
            try:
                with open(lobe_file, "r", encoding="utf-8") as f:
                    content = f.read()

                lobe_name = lobe_file.stem

                # Extract metadata from content
                tags = self._extract_tags_from_content(content)
                entities = self._extract_entities_from_content(content)

                # Index lobe
                self.lobe_index.index_lobe(
                    lobe_id=lobe_name,
                    lobe_name=lobe_name,
                    content=content,
                    file_path=lobe_file,
                    metadata={
                        "module": "core",
                        "status": "active",
                        "tags": tags,
                        "checkpoints": [],
                        "entities": entities,
                        "file_path": str(lobe_file),
                        "file_size": lobe_file.stat().st_size,
                    },
                )
                success_count += 1

            except Exception as e:
                logger.warning(f"Failed to index lobe {lobe_file}: {e}")
                error_count += 1

        self.stats["lobes"] = success_count
        if error_count > 0:
            logger.warning(f"Indexed {success_count} lobes with {error_count} errors")
        else:
            logger.info(f"Indexed {success_count} lobes successfully")

        return success_count > 0

    def _extract_tags_from_content(self, content: str) -> List[str]:
        """Extract tags from manifest content."""
        tags = []

        # Look for tag patterns
        import re

        # Pattern for #tags or @mentions
        tag_pattern = r"[#@][a-zA-Z0-9_\-]+"
        found_tags = re.findall(tag_pattern, content)
        tags.extend(found_tags)

        # Look for metadata sections
        metadata_pattern = r"tags?\s*[:=]\s*\[([^\]]+)\]"
        metadata_match = re.search(metadata_pattern, content, re.IGNORECASE)
        if metadata_match:
            tags_str = metadata_match.group(1)
            tags.extend([t.strip().strip("\"'") for t in tags_str.split(",")])

        return list(set(tags))

    def _extract_entities_from_content(self, content: str) -> List[str]:
        """Extract entities from manifest content."""
        entities = []

        # Simple entity extraction (uppercase words, project names)
        import re

        # Pattern for what looks like entity names
        entity_pattern = r"\b[A-Z][a-zA-Z0-9]+\b"
        found_entities = re.findall(entity_pattern, content)

        # Filter out common words
        common_words = {"The", "This", "That", "These", "Those", "And", "But", "For"}
        entities = [e for e in found_entities if e not in common_words]

        return list(set(entities))

    def verify_migration(self) -> bool:
        """Verify migration success."""
        logger.info("Verifying migration...")

        verifications = []

        # Verify ledger
        try:
            ledger_data = self.ledger_store.read_ledger()
            if ledger_data:
                verifications.append(("ledger", True))
                logger.info("✓ Ledger store verification passed")
            else:
                verifications.append(("ledger", False))
                logger.error("✗ Ledger store verification failed")
        except Exception as e:
            verifications.append(("ledger", False))
            logger.error(f"✗ Ledger store verification error: {e}")

        # Verify manifest count
        try:
            manifest_stats = self.manifest_store.get_stats()
            manifest_count = manifest_stats.get("total_manifests", 0)
            verifications.append(
                ("manifests", manifest_count == self.stats["manifests"])
            )
            if manifest_count == self.stats["manifests"]:
                logger.info(
                    f"✓ Manifest store verification passed ({manifest_count} manifests)"
                )
            else:
                logger.error(
                    f"✗ Manifest store verification failed: expected {self.stats['manifests']}, got {manifest_count}"
                )
        except Exception as e:
            verifications.append(("manifests", False))
            logger.error(f"✗ Manifest store verification error: {e}")

        # Verify lobe index
        try:
            lobe_stats = self.lobe_index.get_stats()
            lobe_count = lobe_stats.get("total_lobes", 0)
            verifications.append(("lobes", lobe_count == self.stats["lobes"]))
            if lobe_count == self.stats["lobes"]:
                logger.info(f"✓ Lobe index verification passed ({lobe_count} lobes)")
            else:
                logger.error(
                    f"✗ Lobe index verification failed: expected {self.stats['lobes']}, got {lobe_count}"
                )
        except Exception as e:
            verifications.append(("lobes", False))
            logger.error(f"✗ Lobe index verification error: {e}")

        # Overall verification
        all_passed = all(passed for _, passed in verifications)

        if all_passed:
            logger.info("✅ All verifications passed!")
        else:
            logger.error("❌ Some verifications failed")

        return all_passed

    def generate_report(self) -> Dict[str, Any]:
        """Generate migration report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats.copy(),
            "backup_location": str(self.backup_dir),
            "stores_initialized": {
                "ledger_store": True,
                "manifest_store": True,
                "lobe_index": True,
            },
            "verification": self.verify_migration(),
        }

        # Calculate duration
        if self.stats["start_time"] and self.stats["end_time"]:
            start_dt = datetime.fromisoformat(self.stats["start_time"])
            end_dt = datetime.fromisoformat(self.stats["end_time"])
            report["duration_seconds"] = (end_dt - start_dt).total_seconds()

        return report

    def run_migration(self) -> bool:
        """Run complete migration process."""
        logger.info("Starting NeoCortex data migration...")

        self.stats["start_time"] = datetime.now().isoformat()

        # Step 1: Backup
        if not self.create_backup():
            logger.error("Backup failed, aborting migration")
            return False

        # Step 2: Migrate data
        migration_steps = [
            ("Ledger", self.migrate_ledger),
            ("Manifests", self.migrate_manifests),
            ("Lobes", self.migrate_lobes),
        ]

        all_success = True
        for step_name, step_func in migration_steps:
            logger.info(f"--- Starting {step_name} migration ---")
            if not step_func():
                logger.error(f"{step_name} migration failed")
                all_success = False
                # Continue with other steps
            logger.info(f"--- Completed {step_name} migration ---")

        self.stats["end_time"] = datetime.now().isoformat()

        # Step 3: Verify
        verification_passed = self.verify_migration()

        # Step 4: Generate report
        report = self.generate_report()

        # Save report
        report_path = self.backup_dir / "migration_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Migration report saved to {report_path}")

        # Final status
        if all_success and verification_passed:
            logger.info("🎉 Migration completed successfully!")
            return True
        else:
            logger.error("Migration completed with errors")
            return False


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("=" * 60)
    print("NeoCortex Data Migration Tool")
    print("=" * 60)
    print("This will migrate existing data to high-performance stores.")
    print("A backup will be created before migration.")
    print()

    # Confirm migration
    try:
        confirm = input("Continue with migration? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Migration cancelled.")
            return 0
    except EOFError:
        print("Migration cancelled (no input).")
        return 0

    # Run migration
    manager = MigrationManager()
    success = manager.run_migration()

    if success:
        print("\n[SUCCESS] Migration successful!")
        print(f"Backup location: {manager.backup_dir}")
        return 0
    else:
        print("\n[FAILED] Migration failed!")
        print("Check logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
