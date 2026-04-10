#!/usr/bin/env python3
"""
Manifest Service - Business logic for manifest management.

This service encapsulates business logic for manifest operations,
using repository interfaces for storage abstraction.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository, CortexRepository, LobeRepository


class ManifestService:
    """Service for manifest business logic."""

    def __init__(
        self,
        ledger_repository: Optional[LedgerRepository] = None,
        cortex_repository: Optional[CortexRepository] = None,
        lobe_repository: Optional[LobeRepository] = None,
    ):
        """
        Initialize manifest service.

        Args:
            ledger_repository: Ledger repository implementation
            cortex_repository: Cortex repository implementation
            lobe_repository: Lobe repository implementation
        """
        if ledger_repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.ledger_repository = FileSystemLedgerRepository()
        else:
            self.ledger_repository = ledger_repository

        if cortex_repository is None:
            from ..repositories import FileSystemCortexRepository

            self.cortex_repository = FileSystemCortexRepository()
        else:
            self.cortex_repository = cortex_repository

        if lobe_repository is None:
            from ..repositories import FileSystemLobeRepository

            self.lobe_repository = FileSystemLobeRepository()
        else:
            self.lobe_repository = lobe_repository

    def _ensure_manifests_structure(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure manifests structure exists in memory cortex."""
        if "memory_cortex" not in ledger:
            ledger["memory_cortex"] = {}

        memory_cortex = ledger["memory_cortex"]

        if "manifests" not in memory_cortex:
            memory_cortex["manifests"] = {}

        return ledger

    def generate_manifest(self, target: str) -> Dict[str, Any]:
        """
        Generate manifest for a cortex or lobe.

        Args:
            target: "cortex" or lobe name

        Returns:
            Dictionary with generated manifest
        """
        if not target:
            return {
                "success": False,
                "error": "target is required (cortex or lobe name)",
            }

        ledger = self.ledger_repository.read_ledger()
        ledger = self._ensure_manifests_structure(ledger)

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex["manifests"]

        # Check if target exists
        if target == "cortex":
            content_source = self.cortex_repository.read_cortex()
            manifest_id = "cortex"
            manifest_type = "cortex"
        else:
            # Assume it's a lobe
            content_source = self.lobe_repository.read_lobe(target)
            if content_source is None:
                return {"success": False, "error": f"Lobe not found: {target}"}
            manifest_id = target
            manifest_type = "lobe"

        # Generate basic manifest
        current_time = datetime.now().isoformat()

        new_manifest = {
            "id": manifest_id,
            "type": manifest_type,
            "created_at": current_time,
            "last_accessed": current_time,
            "last_modified": current_time,
            "metadata": {
                "line_count": len(content_source.split("\n")),
                "has_checkpoints": "- [x]" in content_source
                or "- [ ]" in content_source,
                "has_aliases": "$" in content_source,
                "has_commands": "!" in content_source,
                "has_patterns": "?" in content_source,
                "has_warnings": "!" in content_source
                and "warning" in content_source.lower(),
                "size_chars": len(content_source),
                "word_count": len(content_source.split()),
            },
            "tags": [],
            "entities": [],
            "dependencies": [],
            "status": "active",
        }

        # Extract automatic tags from sections (##)
        lines = content_source.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("## "):
                tag = line[3:].strip()
                if tag and tag not in new_manifest["tags"]:
                    new_manifest["tags"].append(tag)
            elif line.startswith("# "):
                # Main title
                new_manifest["title"] = line[2:].strip()

        # Extract entities (patterns like @entity, $entity)
        import re

        entity_patterns = [
            r"\$(\w+)",  # $ aliases
            r"@(\w+)",  # @ directories
            r"!(\w+)",  # ! commands
            r"\?(\w+)",  # ? patterns
        ]

        for pattern in entity_patterns:
            matches = re.findall(pattern, content_source)
            for match in matches:
                if match not in new_manifest["entities"]:
                    new_manifest["entities"].append(match)

        # Update manifests
        manifests[manifest_id] = new_manifest
        memory_cortex["manifests"] = manifests
        ledger["memory_cortex"] = memory_cortex

        # Write back to ledger
        success = self.ledger_repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "manifest": new_manifest,
                "message": f"Manifest generated for {target}",
                "manifest_id": manifest_id,
                "type": manifest_type,
                "timestamp": current_time,
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def update_manifest(
        self, manifest_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update manifest metadata.

        Args:
            manifest_id: Manifest ID to update
            metadata: Optional metadata dictionary to merge

        Returns:
            Dictionary with update result
        """
        if not manifest_id:
            return {"success": False, "error": "manifest_id is required"}

        ledger = self.ledger_repository.read_ledger()

        if "memory_cortex" not in ledger:
            return {"success": False, "error": "memory_cortex not found in ledger"}

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex.get("manifests", {})

        if manifest_id not in manifests:
            return {"success": False, "error": f"Manifest not found: {manifest_id}"}

        # Update manifest
        manifest = manifests[manifest_id]
        current_time = datetime.now().isoformat()

        manifest["last_accessed"] = current_time
        manifest["last_modified"] = current_time

        # Merge metadata if provided
        if metadata:
            if "metadata" not in manifest:
                manifest["metadata"] = {}
            manifest["metadata"].update(metadata)

        manifests[manifest_id] = manifest
        memory_cortex["manifests"] = manifests
        ledger["memory_cortex"] = memory_cortex

        # Write back to ledger
        success = self.ledger_repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "manifest": manifest,
                "message": f"Manifest {manifest_id} updated",
                "manifest_id": manifest_id,
                "timestamp": current_time,
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def query_manifests(
        self,
        search_term: Optional[str] = None,
        manifest_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Query manifests by various criteria.

        Args:
            search_term: Text to search in tags, entities, type
            manifest_type: Filter by type ("cortex" or "lobe")
            tags: Filter by tags
            limit: Maximum results to return

        Returns:
            Dictionary with query results
        """
        ledger = self.ledger_repository.read_ledger()

        if "memory_cortex" not in ledger:
            return {
                "success": True,
                "query": {
                    "search_term": search_term,
                    "type": manifest_type,
                    "tags": tags,
                },
                "results": [],
                "count": 0,
                "message": "No manifests found (memory_cortex not present)",
            }

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex.get("manifests", {})

        results = []
        for manifest_id, manifest in manifests.items():
            # Apply filters
            matches = True

            # Type filter
            if manifest_type and manifest.get("type") != manifest_type:
                matches = False

            # Tags filter
            if tags and matches:
                manifest_tags = manifest.get("tags", [])
                tag_match = any(tag in manifest_tags for tag in tags)
                if not tag_match:
                    matches = False

            # Search term filter
            if search_term and matches:
                search_term_lower = search_term.lower()
                found = False

                # Search in tags
                for tag in manifest.get("tags", []):
                    if search_term_lower in tag.lower():
                        found = True
                        break

                # Search in entities
                if not found:
                    for entity in manifest.get("entities", []):
                        if search_term_lower in str(entity).lower():
                            found = True
                            break

                # Search in type
                if not found:
                    manifest_type_str = manifest.get("type", "")
                    if search_term_lower in manifest_type_str.lower():
                        found = True

                # Search in title if exists
                if not found and "title" in manifest:
                    if search_term_lower in manifest["title"].lower():
                        found = True

                if not found:
                    matches = False

            if matches:
                results.append(manifest)

        # Apply limit
        if limit > 0 and len(results) > limit:
            results = results[:limit]

        return {
            "success": True,
            "query": {
                "search_term": search_term,
                "type": manifest_type,
                "tags": tags,
                "limit": limit,
            },
            "results": results,
            "count": len(results),
            "total_manifests": len(manifests),
        }

    def get_manifest(self, manifest_id: str) -> Dict[str, Any]:
        """
        Get a specific manifest.

        Args:
            manifest_id: Manifest ID

        Returns:
            Dictionary with manifest
        """
        if not manifest_id:
            return {"success": False, "error": "manifest_id is required"}

        ledger = self.ledger_repository.read_ledger()

        if "memory_cortex" not in ledger:
            return {"success": False, "error": "memory_cortex not found in ledger"}

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex.get("manifests", {})

        if manifest_id not in manifests:
            return {"success": False, "error": f"Manifest not found: {manifest_id}"}

        manifest = manifests[manifest_id]

        # Update last accessed time
        current_time = datetime.now().isoformat()
        manifest["last_accessed"] = current_time
        manifests[manifest_id] = manifest

        # Write back to ledger
        memory_cortex["manifests"] = manifests
        ledger["memory_cortex"] = memory_cortex
        self.ledger_repository.write_ledger(ledger)

        return {
            "success": True,
            "manifest": manifest,
            "manifest_id": manifest_id,
            "exists": True,
            "accessed_at": current_time,
        }

    def delete_manifest(self, manifest_id: str) -> Dict[str, Any]:
        """
        Delete a manifest.

        Args:
            manifest_id: Manifest ID to delete

        Returns:
            Dictionary with deletion result
        """
        if not manifest_id:
            return {"success": False, "error": "manifest_id is required"}

        ledger = self.ledger_repository.read_ledger()

        if "memory_cortex" not in ledger:
            return {"success": False, "error": "memory_cortex not found in ledger"}

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex.get("manifests", {})

        if manifest_id not in manifests:
            return {"success": False, "error": f"Manifest not found: {manifest_id}"}

        # Remove manifest
        deleted_manifest = manifests.pop(manifest_id)
        memory_cortex["manifests"] = manifests
        ledger["memory_cortex"] = memory_cortex

        # Write back to ledger
        success = self.ledger_repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "deleted_manifest": deleted_manifest,
                "message": f"Manifest {manifest_id} deleted",
                "manifest_id": manifest_id,
                "remaining_manifests": len(manifests),
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def list_all_manifests(self) -> Dict[str, Any]:
        """
        List all manifests.

        Returns:
            Dictionary with all manifests
        """
        ledger = self.ledger_repository.read_ledger()

        if "memory_cortex" not in ledger:
            return {
                "success": True,
                "manifests": {},
                "count": 0,
                "message": "No manifests found (memory_cortex not present)",
            }

        memory_cortex = ledger["memory_cortex"]
        manifests = memory_cortex.get("manifests", {})

        # Categorize manifests
        cortex_manifests = {}
        lobe_manifests = {}

        for manifest_id, manifest in manifests.items():
            manifest_type = manifest.get("type", "unknown")
            if manifest_type == "cortex":
                cortex_manifests[manifest_id] = manifest
            elif manifest_type == "lobe":
                lobe_manifests[manifest_id] = manifest

        return {
            "success": True,
            "manifests": manifests,
            "cortex_manifests": cortex_manifests,
            "lobe_manifests": lobe_manifests,
            "count": len(manifests),
            "cortex_count": len(cortex_manifests),
            "lobe_count": len(lobe_manifests),
            "last_updated": datetime.now().isoformat(),
        }

    def generate_all_manifests(self) -> Dict[str, Any]:
        """
        Generate manifests for all lobes and cortex.

        Returns:
            Dictionary with generation results
        """
        results = {"generated": [], "failed": [], "skipped": []}

        # Generate cortex manifest
        cortex_result = self.generate_manifest("cortex")
        if cortex_result["success"]:
            results["generated"].append("cortex")
        else:
            results["failed"].append(
                {"target": "cortex", "error": cortex_result.get("error")}
            )

        # Generate lobe manifests
        lobe_names = self.lobe_repository.list_lobes()
        for lobe_name in lobe_names:
            # Check if manifest already exists
            ledger = self.ledger_repository.read_ledger()
            if "memory_cortex" in ledger:
                memory_cortex = ledger["memory_cortex"]
                manifests = memory_cortex.get("manifests", {})
                if lobe_name in manifests:
                    results["skipped"].append(lobe_name)
                    continue

            # Generate manifest
            lobe_result = self.generate_manifest(lobe_name)
            if lobe_result["success"]:
                results["generated"].append(lobe_name)
            else:
                results["failed"].append(
                    {"target": lobe_name, "error": lobe_result.get("error")}
                )

        return {
            "success": True,
            "results": results,
            "total_generated": len(results["generated"]),
            "total_failed": len(results["failed"]),
            "total_skipped": len(results["skipped"]),
            "message": f"Generated {len(results['generated'])} manifests, failed {len(results['failed'])}, skipped {len(results['skipped'])}",
        }


# Singleton instance for convenience
_default_manifest_service = None


def get_manifest_service(
    ledger_repository: Optional[LedgerRepository] = None,
    cortex_repository: Optional[CortexRepository] = None,
    lobe_repository: Optional[LobeRepository] = None,
) -> ManifestService:
    """
    Get manifest service instance (singleton pattern).

    Args:
        ledger_repository: Optional ledger repository implementation
        cortex_repository: Optional cortex repository implementation
        lobe_repository: Optional lobe repository implementation

    Returns:
        ManifestService instance
    """
    global _default_manifest_service

    if (
        ledger_repository is not None
        or cortex_repository is not None
        or lobe_repository is not None
    ):
        return ManifestService(ledger_repository, cortex_repository, lobe_repository)

    if _default_manifest_service is None:
        _default_manifest_service = ManifestService()

    return _default_manifest_service
