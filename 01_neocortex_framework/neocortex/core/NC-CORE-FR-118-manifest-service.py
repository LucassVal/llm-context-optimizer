# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""
Manifest Service - Business logic for manifest management.

This service encapsulates business logic for manifest operations,
using repository interfaces for storage abstraction.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any

from ..repositories import CortexRepository, LedgerRepository, LobeRepository


def _parse_yaml_string(yaml_str: str) -> dict[str, Any]:
    """
    Parse YAML string using available YAML parser (ruamel.yaml, PyYAML, or regex fallback).

    Args:
        yaml_str: YAML string to parse

    Returns:
        Parsed dictionary
    """
    # Try ruamel.yaml first
    try:
        import ruamel.yaml

        yaml = ruamel.yaml.YAML(typ="safe")
        return yaml.load(yaml_str) or {}
    except ImportError:
        pass
    except Exception:
        # ruamel.yaml is installed but parsing failed
        pass

    # Try PyYAML
    try:
        import yaml

        return yaml.safe_load(yaml_str) or {}
    except ImportError:
        pass
    except Exception:
        # PyYAML is installed but parsing failed
        pass

    # Regex fallback (simple key: value)
    result = {}
    pattern = r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*?)\s*(?:#.*)?$"
    for line in yaml_str.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(pattern, line)
        if match:
            key = match.group(1)
            value_str = match.group(2).strip()
            # Try to parse value (int, float, bool, string)
            if value_str.lower() in ("true", "false"):
                value = value_str.lower() == "true"
            elif value_str.isdigit():
                value = int(value_str)
            elif re.match(r"^-?\d+\.\d+$", value_str):
                value = float(value_str)
            elif (value_str.startswith('"') and value_str.endswith('"')) or (value_str.startswith("'") and value_str.endswith("'")):
                value = value_str[1:-1]
            else:
                value = value_str
            result[key] = value
    return result


def _extract_frontmatter(content: str) -> dict[str, Any]:
    """
    Extract YAML frontmatter from Python or Markdown content.

    Frontmatter pattern:
        ---
        key: value
        ---
    or within a docstring for Python files:
        \"\"\"---
        key: value
        ---\"\"\"

    Args:
        content: File content

    Returns:
        Extracted frontmatter dictionary
    """
    if not content:
        return {}

    lines = content.splitlines()
    if not lines:
        return {}

    # Check for opening pattern
    first_line = lines[0].strip()
    if first_line.startswith("---"):
        start_index = 0
        opening_pattern = "---"
    elif first_line.startswith('"""---'):
        start_index = 0
        opening_pattern = '"""---'
    else:
        # No frontmatter
        return {}

    # Find closing pattern
    closing_pattern = "---" if opening_pattern == "---" else '---"""'
    for i in range(start_index + 1, len(lines)):
        line = lines[i].strip()
        if line == closing_pattern:
            # Extract YAML lines between start_index+1 and i-1
            yaml_lines = lines[start_index + 1 : i]
            yaml_str = "\n".join(yaml_lines)
            return _parse_yaml_string(yaml_str)

    # No closing pattern found
    return {}


def _sanitize_for_json(obj):
    """
    Recursively sanitize objects for JSON serialization.

    Converts datetime.date, datetime.datetime, and other non-serializable
    objects to string representations.
    """
    import datetime

    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_sanitize_for_json(item) for item in obj)
    elif isinstance(obj, set):
        return [_sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        # Fallback: convert to string
        return str(obj)


class ManifestService:
    """Service for manifest business logic."""

    def __init__(
        self,
        ledger_repository: LedgerRepository | None = None,
        cortex_repository: CortexRepository | None = None,
        lobe_repository: LobeRepository | None = None,
    ):
        """
        Initialize manifest service.

        Args:
            ledger_repository: Ledger repository implementation
            cortex_repository: Cortex repository implementation
            lobe_repository: Lobe repository implementation
        """
        if ledger_repository is None:
            from ..infra.ledger_store import LedgerStore

            self.ledger_repository = LedgerStore()
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

    def _ensure_manifests_structure(self, ledger: dict[str, Any]) -> dict[str, Any]:
        """Ensure manifests structure exists in memory cortex."""
        if "memory_cortex" not in ledger:
            ledger["memory_cortex"] = {}

        memory_cortex = ledger["memory_cortex"]

        if "manifests" not in memory_cortex:
            memory_cortex["manifests"] = {}

        return ledger

    def generate(self, target: str = "") -> dict[str, Any]:
        """Alias for generate_manifest."""
        return self.generate_manifest(target or "all")

    def generate_manifest(self, target: str) -> dict[str, Any]:
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

        # Extract frontmatter YAML from content
        frontmatter = _extract_frontmatter(content_source)

        # Base manifest structure
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

        # Enrich with frontmatter fields
        if frontmatter:
            # Map standard frontmatter fields to manifest fields
            # domain, layer, type (file type), tier, parent, children, dependence, codependence
            for field in [
                "domain",
                "layer",
                "tier",
                "parent",
                "children",
                "dependence",
                "codependence",
            ]:
                if field in frontmatter:
                    new_manifest[field] = frontmatter[field]
            # Frontmatter 'type' is file type, store as 'file_type' to avoid conflict
            if "type" in frontmatter:
                new_manifest["file_type"] = frontmatter["type"]
            # Frontmatter tags extend the tags list
            if "tags" in frontmatter:
                if isinstance(frontmatter["tags"], list):
                    new_manifest["tags"].extend(frontmatter["tags"])
                else:
                    new_manifest["tags"].append(frontmatter["tags"])
            # Hash if present
            if "hash" in frontmatter:
                new_manifest["hash"] = frontmatter["hash"]
            # Any other frontmatter fields go into metadata.frontmatter
            frontmatter_metadata = {
                k: v
                for k, v in frontmatter.items()
                if k
                not in [
                    "domain",
                    "layer",
                    "type",
                    "tier",
                    "parent",
                    "children",
                    "dependence",
                    "codependence",
                    "tags",
                    "hash",
                ]
            }
            if frontmatter_metadata:
                new_manifest.setdefault("frontmatter", {}).update(frontmatter_metadata)

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

        # Deduplicate tags and entities
        if "tags" in new_manifest and isinstance(new_manifest["tags"], list):
            seen = set()
            unique_tags = []
            for tag in new_manifest["tags"]:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            new_manifest["tags"] = unique_tags
        if "entities" in new_manifest and isinstance(new_manifest["entities"], list):
            seen = set()
            unique_entities = []
            for entity in new_manifest["entities"]:
                if entity not in seen:
                    seen.add(entity)
                    unique_entities.append(entity)
            new_manifest["entities"] = unique_entities

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
        self, manifest_id: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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
        search_term: str | None = None,
        manifest_type: str | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
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
        for _manifest_id, manifest in manifests.items():
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
                if not found and "title" in manifest and search_term_lower in manifest["title"].lower():
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

    def get_manifest(self, manifest_id: str) -> dict[str, Any]:
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

    def delete_manifest(self, manifest_id: str) -> dict[str, Any]:
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

    def list_all_manifests(self) -> dict[str, Any]:
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

    def generate_all_manifests(self) -> dict[str, Any]:
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

    def vector_scan(
        self, root_dir: str | None = None, output_file: str | None = None
    ) -> dict[str, Any]:
        """
        Perform vector scanning of YAML frontmatter headers across all files.

        Scans for YAML Header T007 blocks in .mdc, .py, etc files and indexes relationships.

        Args:
            root_dir: Root directory to scan (defaults to workspace root)
            output_file: Path to save indexed extraction (defaults to NC-IDX-FR-001-graph-extraction.json)

        Returns:
            Dictionary with scan results and extracted graph
        """

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logger = logging.getLogger(__name__)

        try:
            if root_dir is None:
                # Default to parent directory of this file's project root
                root_dir = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..", "..")
                )
            if output_file is None:
                output_file = os.path.join(
                    root_dir, "NC-IDX-FR-001-graph-extraction.json"
                )

            logger.info(f"Starting vector scan from root: {root_dir}")

            # Supported extensions
            extensions = {".mdc", ".py", ".md", ".yaml", ".yml", ".json", ".txt"}

            extracted_data = []
            relationship_graph = {
                "nodes": [],
                "edges": [],
                "tags": {},
                "codependence": [],
                "parent_child": [],
            }

            file_count = 0
            error_count = 0

            for dirpath, dirnames, filenames in os.walk(root_dir):
                # Skip hidden directories and certain patterns
                dirnames[:] = [
                    d
                    for d in dirnames
                    if not d.startswith(".")
                    and d not in {"__pycache__", "node_modules"}
                ]

                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in extensions:
                        continue

                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir)

                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        frontmatter = _extract_frontmatter(content)

                        # Extract key relationship fields
                        node_id = relative_path.replace("\\", "/")
                        # Extract topology fields
                        topology = frontmatter.get("topology", {})
                        all_fields = {**frontmatter, **topology}
                        node = {
                            "id": node_id,
                            "path": relative_path,
                            "frontmatter": frontmatter,
                            "type": ext,
                            "size": len(content),
                            "has_codependence": "codependence" in all_fields,
                            "has_parent": "parent" in all_fields,
                            "has_dependence": "dependence" in all_fields,
                            "has_children": "children" in all_fields,
                        }

                        extracted_data.append(node)

                        # Build relationship graph
                        if frontmatter:
                            # Add tags to tag index
                            tags = frontmatter.get("tags", [])
                            if isinstance(tags, str):
                                tags = [tags]
                            for tag in tags:
                                relationship_graph["tags"].setdefault(tag, []).append(
                                    node_id
                                )

                            # Extract topology fields
                            topology = frontmatter.get("topology", {})
                            # Merge topology with frontmatter (topology takes precedence)
                            all_fields = {**frontmatter, **topology}

                            # Codependence relationships
                            codependence = all_fields.get("codependence", [])
                            if isinstance(codependence, str):
                                codependence = [codependence]
                            for dep in codependence:
                                relationship_graph["codependence"].append(
                                    {
                                        "source": node_id,
                                        "target": dep,
                                        "type": "codependence",
                                    }
                                )

                            # Parent-child relationships
                            parent = all_fields.get("parent")
                            if parent:
                                relationship_graph["parent_child"].append(
                                    {
                                        "child": node_id,
                                        "parent": parent,
                                        "type": "parent_child",
                                    }
                                )

                            # Children relationships (reverse of parent)
                            children = all_fields.get("children", [])
                            if isinstance(children, str):
                                children = [children]
                            for child in children:
                                relationship_graph["parent_child"].append(
                                    {
                                        "child": child,
                                        "parent": node_id,
                                        "type": "parent_child",
                                    }
                                )

                            # Dependence relationships
                            dependence = all_fields.get("dependence", [])
                            if isinstance(dependence, str):
                                dependence = [dependence]
                            for dep in dependence:
                                relationship_graph["edges"].append(
                                    {
                                        "source": node_id,
                                        "target": dep,
                                        "type": "dependence",
                                    }
                                )

                        file_count += 1
                        if file_count % 100 == 0:
                            logger.info(f"Processed {file_count} files...")

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing {file_path}: {e}")
                        continue

            logger.info(
                f"Scan completed. Processed {file_count} files, errors: {error_count}"
            )

            # Save extracted data
            output_data = {
                "scan_timestamp": datetime.now().isoformat(),
                "root_dir": root_dir,
                "file_count": file_count,
                "error_count": error_count,
                "extracted_nodes": extracted_data,
                "relationship_graph": relationship_graph,
            }

            try:
                # Sanitize data for JSON serialization
                sanitized_data = _sanitize_for_json(output_data)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(sanitized_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Extraction saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save extraction: {e}")
                return {
                    "success": False,
                    "error": f"Failed to save extraction: {e}",
                    "processed_files": file_count,
                    "errors": error_count,
                }

            return {
                "success": True,
                "message": f"Vector scan completed. Processed {file_count} files, errors {error_count}",
                "output_file": output_file,
                "file_count": file_count,
                "error_count": error_count,
                "extracted_nodes_count": len(extracted_data),
                "relationship_graph_summary": {
                    "nodes": len(extracted_data),
                    "edges": len(relationship_graph["edges"]),
                    "codependence_relations": len(relationship_graph["codependence"]),
                    "parent_child_relations": len(relationship_graph["parent_child"]),
                    "unique_tags": len(relationship_graph["tags"]),
                },
            }

        except Exception as e:
            logger.error(f"Vector scan failed: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance for convenience
_default_manifest_service = None


def get_manifest_service(
    ledger_repository: LedgerRepository | None = None,
    cortex_repository: CortexRepository | None = None,
    lobe_repository: LobeRepository | None = None,
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


def _test_frontmatter_extraction():
    """Test frontmatter extraction logic."""
    test_content = '''"""---
domain: "core"
layer: "core"
type: "file"
tags: ["manifest", "service"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
Test file.
"""
'''
    result = _extract_frontmatter(test_content)
    print("Extracted frontmatter:", result)
    assert result.get("domain") == "core"
    assert result.get("layer") == "core"
    assert result.get("type") == "file"
    assert "manifest" in result.get("tags", [])
    print("OK Frontmatter extraction test passed")

    # Test without frontmatter
    no_fm = "No frontmatter here."
    result2 = _extract_frontmatter(no_fm)
    assert result2 == {}
    print("OK No frontmatter test passed")

    # Test with simple --- delimiters
    simple = """---
domain: infra
---
content"""
    result3 = _extract_frontmatter(simple)
    assert result3.get("domain") == "infra"
    print("OK Simple delimiter test passed")

    # Test nested structures in YAML (list of dicts)
    nested = """---
domain: test
children:
  - name: child1
    type: file
  - name: child2
    type: service
dependence:
  - required: lib1
    version: 1.0
---
content"""
    result4 = _extract_frontmatter(nested)
    print("Nested frontmatter:", result4)
    assert result4.get("domain") == "test"
    assert isinstance(result4.get("children"), list)
    assert len(result4["children"]) == 2
    assert result4["children"][0]["name"] == "child1"
    assert isinstance(result4.get("dependence"), list)
    print("OK Nested YAML test passed")

    print("All frontmatter tests passed successfully.")


def _test_manifest_enrichment():
    """Test manifest enrichment with frontmatter."""
    from unittest.mock import Mock

    # Mock ledger repository
    ledger_repo = Mock()
    ledger_repo.read_ledger.return_value = {}
    ledger_repo.write_ledger.return_value = True
    # Mock cortex repository with frontmatter content
    cortex_repo = Mock()
    cortex_repo.read_cortex.return_value = '''"""---
domain: "core"
layer: "core"
type: "file"
tags: ["manifest", "service"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
Cortex content.
"""
'''
    # Create service
    service = ManifestService(
        ledger_repository=ledger_repo, cortex_repository=cortex_repo
    )
    result = service.generate_manifest("cortex")
    assert result["success"]
    manifest = result["manifest"]
    print("Generated manifest:", manifest)
    assert manifest["domain"] == "core"
    assert manifest["layer"] == "core"
    assert manifest["file_type"] == "file"
    assert "manifest" in manifest["tags"]
    assert "service" in manifest["tags"]
    print("OK Manifest enrichment test passed")


if __name__ == "__main__":
    _test_frontmatter_extraction()
    _test_manifest_enrichment()
