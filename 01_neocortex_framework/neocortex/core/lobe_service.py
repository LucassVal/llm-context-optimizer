#!/usr/bin/env python3
"""
Lobe Service - Business logic for lobe operations.

This service encapsulates business logic for lobe operations,
using repository interfaces for storage abstraction.
"""

import re
from typing import Dict, Any, List, Optional
from ..repositories import LobeRepository
from .ledger_service import get_ledger_service
from ..infra.lobe_index import LobeIndexService


class LobeService:
    """Service for lobe-related business logic."""

    def __init__(
        self,
        repository: Optional[LobeRepository] = None,
        index: Optional[LobeIndexService] = None,
    ):
        """
        Initialize lobe service.

        Args:
            repository: Lobe repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLobeRepository.
            index: Lobe index service for fast search operations.
                   If None, creates a default LobeIndexService.
        """
        if repository is None:
            from ..repositories import FileSystemLobeRepository

            self.repository = FileSystemLobeRepository()
        else:
            self.repository = repository

        if index is None:
            self.index = LobeIndexService()
        else:
            self.index = index

    def list_lobes(self) -> Dict[str, Any]:
        """
        List all available lobes with metadata.

        Returns:
            Dictionary with lobe list and metadata
        """
        lobe_names = self.repository.list_lobes()

        lobes = []
        for name in lobe_names:
            content = self.repository.read_lobe(name)
            if content:
                metadata = self._extract_lobe_metadata(name, content)
                lobes.append({"name": name, **metadata})

        return {
            "lobes": lobes,
            "total": len(lobes),
            "categories": self._categorize_lobes(lobes),
        }

    def get_lobe(self, lobe_name: str) -> Dict[str, Any]:
        """
        Get a specific lobe with content and metadata.

        Args:
            lobe_name: Name of the lobe

        Returns:
            Lobe dictionary with content and metadata
        """
        content = self.repository.read_lobe(lobe_name)

        if content is None:
            return {
                "name": lobe_name,
                "exists": False,
                "error": f"Lobe '{lobe_name}' not found",
            }

        metadata = self._extract_lobe_metadata(lobe_name, content)

        return {"name": lobe_name, "exists": True, "content": content, **metadata}

    def create_lobe(
        self, lobe_name: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new lobe.

        Args:
            lobe_name: Name of the lobe (should end with .mdc)
            content: Lobe content
            metadata: Optional metadata for the lobe

        Returns:
            Creation result dictionary
        """
        # Validate lobe name
        if not lobe_name.endswith(".mdc"):
            lobe_name = f"{lobe_name}.mdc"

        # Check if lobe already exists
        if self.repository.lobe_exists(lobe_name):
            return {"success": False, "error": f"Lobe '{lobe_name}' already exists"}

        # Validate content
        if not content.strip():
            return {"success": False, "error": "Lobe content cannot be empty"}

        # Ensure content has proper header
        if not content.startswith("#"):
            content = f"# {lobe_name.replace('.mdc', '')}\n\n{content}"

        # Add metadata as comments if provided
        if metadata:
            metadata_comments = "\n".join(
                [f"<!-- {k}: {v} -->" for k, v in metadata.items()]
            )
            content = f"{metadata_comments}\n\n{content}"

        # Write lobe
        success = self.repository.write_lobe(lobe_name, content)

        if success:
            extracted_metadata = self._extract_lobe_metadata(lobe_name, content)

            # Update search index
            try:
                self.index.index_lobe(lobe_name)
            except Exception as e:
                import logging

                logging.getLogger(__name__).warning(
                    f"Failed to index lobe '{lobe_name}': {e}"
                )

            return {
                "success": True,
                "message": f"Lobe '{lobe_name}' created successfully",
                "name": lobe_name,
                "metadata": extracted_metadata,
                "size_chars": len(content),
                "lines": content.count("\n") + 1,
            }
        else:
            return {"success": False, "error": f"Failed to create lobe '{lobe_name}'"}

    def update_lobe(self, lobe_name: str, content: str) -> Dict[str, Any]:
        """
        Update an existing lobe.

        Args:
            lobe_name: Name of the lobe
            content: New lobe content

        Returns:
            Update result dictionary
        """
        # Check if lobe exists
        if not self.repository.lobe_exists(lobe_name):
            return {"success": False, "error": f"Lobe '{lobe_name}' does not exist"}

        # Validate content
        if not content.strip():
            return {"success": False, "error": "Lobe content cannot be empty"}

        # Write updated lobe
        success = self.repository.write_lobe(lobe_name, content)

        if success:
            extracted_metadata = self._extract_lobe_metadata(lobe_name, content)

            # Update search index - delete old entry first to ensure clean update
            import logging

            try:
                # Compute lobe_id same way as LobeIndexService does
                lobe_id = lobe_name.replace(".mdc", "").replace("/", "_")
                # Delete old index entry if it exists
                try:
                    self.index.index.delete_lobe(lobe_id)
                except Exception as delete_err:
                    logging.getLogger(__name__).debug(
                        f"Could not delete old index entry for {lobe_id}: {delete_err}"
                    )

                # Index updated lobe
                if self.index.index_lobe(lobe_name):
                    logging.getLogger(__name__).debug(
                        f"Indexed lobe '{lobe_name}' successfully"
                    )
                else:
                    logging.getLogger(__name__).warning(
                        f"Indexing lobe '{lobe_name}' returned False"
                    )
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"Failed to index lobe '{lobe_name}': {e}"
                )

            return {
                "success": True,
                "message": f"Lobe '{lobe_name}' updated successfully",
                "name": lobe_name,
                "metadata": extracted_metadata,
                "size_chars": len(content),
                "lines": content.count("\n") + 1,
            }
        else:
            return {"success": False, "error": f"Failed to update lobe '{lobe_name}'"}

    def delete_lobe(self, lobe_name: str) -> Dict[str, Any]:
        """
        Delete a lobe.

        Args:
            lobe_name: Name of the lobe

        Returns:
            Deletion result dictionary
        """
        # Note: This implementation assumes the repository supports deletion.
        # FileSystemLobeRepository doesn't have delete method yet.
        # For now, we'll return a not implemented error.

        return {
            "success": False,
            "error": "Lobe deletion not implemented in current repository",
            "note": "Lobes should be archived rather than deleted",
        }

    def search_lobes(self, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for text across all lobes using LobeIndex for fast retrieval.

        Args:
            query: Text to search for
            case_sensitive: Whether search is case-sensitive

        Returns:
            Search results dictionary
        """
        try:
            # Use LobeIndex to find lobes that match the query (full-text search)
            # Limit to 1000 results to avoid excessive memory usage
            index_results = self.index.search_lobes(query=query, limit=1000)
        except Exception as e:
            # Fallback to linear scan if index fails
            import logging

            logging.getLogger(__name__).warning(
                f"LobeIndex search failed: {e}, falling back to linear scan"
            )
            index_results = []

        # If index returned no results, fallback to linear scan across all lobes
        if not index_results:
            lobe_names = self.repository.list_lobes()
            candidate_lobes = [{"lobe_name": name} for name in lobe_names]
        else:
            candidate_lobes = index_results

        results = []
        for candidate in candidate_lobes:
            lobe_name = candidate.get("lobe_name", candidate.get("lobe_id", ""))
            if not lobe_name:
                continue

            # Get content from index result if available, otherwise from repository
            content = candidate.get("content")
            if not content:
                content = self.repository.read_lobe(lobe_name)
                if not content:
                    continue

            # Find all matches within content respecting case_sensitive flag
            if case_sensitive:
                matches = list(re.finditer(re.escape(query), content))
            else:
                matches = list(re.finditer(re.escape(query), content, re.IGNORECASE))

            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]

                line_number = content[: match.start()].count("\n") + 1

                results.append(
                    {
                        "lobe": lobe_name,
                        "position": match.start(),
                        "line": line_number,
                        "context": context,
                        "match": match.group(),
                    }
                )

        return {
            "query": query,
            "case_sensitive": case_sensitive,
            "total_matches": len(results),
            "results_by_lobe": self._group_results_by_lobe(results),
            "results": results,
        }

    def get_lobe_patterns(self, lobe_name: str) -> Dict[str, Any]:
        """
        Extract patterns (symbols starting with ?) from a lobe.

        Args:
            lobe_name: Name of the lobe

        Returns:
            Dictionary with extracted patterns
        """
        content = self.repository.read_lobe(lobe_name)

        if content is None:
            return {"lobe": lobe_name, "exists": False, "patterns": []}

        # Extract patterns (e.g., ?jwt, ?auth, ?secure-token)
        pattern_regex = r"\?(\w+(-\w+)*)"
        patterns = list(set(re.findall(pattern_regex, content)))

        # Flattern tuple matches
        patterns = [p[0] if isinstance(p, tuple) else p for p in patterns]

        return {
            "lobe": lobe_name,
            "exists": True,
            "patterns": patterns,
            "count": len(patterns),
        }

    def _extract_lobe_metadata(self, lobe_name: str, content: str) -> Dict[str, Any]:
        """Extract metadata from lobe content."""
        metadata = {
            "size_chars": len(content),
            "lines": content.count("\n") + 1,
            "has_aliases": "$" in content,
            "has_patterns": "?" in content,
            "has_commands": "@" in content,
            "has_warnings": "!" in content,
        }

        # Extract title from first line
        lines = content.split("\n")
        if lines and lines[0].startswith("#"):
            metadata["title"] = lines[0].replace("#", "").strip()

        # Count sections
        section_count = sum(1 for line in lines if line.strip().startswith("##"))
        metadata["sections"] = section_count

        # Extract metadata from comments
        comment_pattern = r"<!--\s*([^:]+):\s*(.+?)\s*-->"
        for match in re.findall(comment_pattern, content):
            key = match[0].strip().lower().replace(" ", "_")
            value = match[1].strip()
            metadata[key] = value

        return metadata

    def _categorize_lobes(self, lobes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize lobes based on name patterns."""
        categories = {
            "framework": [],  # NC-CTX-, NC-LED-, etc.
            "agent": [],  # NC-LBE- (lobe)
            "template": [],  # Template files
            "phase": [],  # Phase-specific lobes
            "other": [],
        }

        for lobe in lobes:
            name = lobe["name"]

            if name.startswith("NC-CTX-") or name.startswith("NC-LED-"):
                categories["framework"].append(name)
            elif name.startswith("NC-LBE-"):
                categories["agent"].append(name)
            elif "template" in name.lower():
                categories["template"].append(name)
            elif "phase" in name.lower():
                categories["phase"].append(name)
            else:
                categories["other"].append(name)

        return categories

    def _group_results_by_lobe(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group search results by lobe name."""
        grouped = {}
        for result in results:
            lobe = result["lobe"]
            if lobe not in grouped:
                grouped[lobe] = []
            grouped[lobe].append(result)
        return grouped

    def get_active_lobes(self) -> Dict[str, Any]:
        """
        Get list of active lobes from ledger.

        Returns:
            Dictionary with active lobes information
        """
        ledger_service = get_ledger_service()
        ledger = ledger_service.get_full_ledger()

        memory_cortex = ledger.get("memory_cortex", {})
        active_lobes = memory_cortex.get("active_lobes", [])

        # Get lobe details for active lobes
        lobe_details = []
        for lobe_name in active_lobes:
            lobe_content = self.repository.read_lobe(lobe_name)
            if lobe_content:
                metadata = self._extract_lobe_metadata(lobe_name, lobe_content)
                lobe_details.append({"name": lobe_name, **metadata})
            else:
                lobe_details.append(
                    {
                        "name": lobe_name,
                        "exists": False,
                        "error": f"Lobe file not found: {lobe_name}",
                    }
                )

        return {
            "active_lobes": active_lobes,
            "lobe_details": lobe_details,
            "total_active": len(active_lobes),
            "has_memory_cortex": "memory_cortex" in ledger,
        }

    def activate_lobe(self, lobe_name: str) -> Dict[str, Any]:
        """
        Activate a lobe (add to active lobes in memory cortex).

        Args:
            lobe_name: Name of the lobe to activate

        Returns:
            Dictionary with activation result
        """
        # Check if lobe exists
        if not self.repository.lobe_exists(lobe_name):
            return {"success": False, "error": f"Lobe '{lobe_name}' does not exist"}

        ledger_service = get_ledger_service()
        ledger = ledger_service.get_full_ledger()

        # Ensure memory_cortex structure exists
        if "memory_cortex" not in ledger:
            ledger["memory_cortex"] = {}

        memory_cortex = ledger["memory_cortex"]

        if "active_lobes" not in memory_cortex:
            memory_cortex["active_lobes"] = []

        active_lobes = memory_cortex["active_lobes"]

        # Check if already active
        if lobe_name in active_lobes:
            return {
                "success": True,
                "already_active": True,
                "message": f"Lobe '{lobe_name}' is already active",
                "active_lobes": active_lobes,
            }

        # Add to active lobes
        active_lobes.append(lobe_name)
        memory_cortex["active_lobes"] = active_lobes
        ledger["memory_cortex"] = memory_cortex

        # Update ledger
        success = ledger_service.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "lobe_name": lobe_name,
                "activated": True,
                "active_lobes": active_lobes,
                "total_active": len(active_lobes),
                "message": f"Lobe '{lobe_name}' activated successfully",
            }
        else:
            return {"success": False, "error": "Failed to update ledger"}

    def deactivate_lobe(self, lobe_name: str) -> Dict[str, Any]:
        """
        Deactivate a lobe (remove from active lobes in memory cortex).

        Args:
            lobe_name: Name of the lobe to deactivate

        Returns:
            Dictionary with deactivation result
        """
        ledger_service = get_ledger_service()
        ledger = ledger_service.get_full_ledger()

        # Check if memory_cortex exists
        if "memory_cortex" not in ledger:
            return {
                "success": False,
                "error": "memory_cortex not found in ledger",
                "note": "No active lobes to deactivate from",
            }

        memory_cortex = ledger["memory_cortex"]
        active_lobes = memory_cortex.get("active_lobes", [])

        # Check if lobe is active
        if lobe_name not in active_lobes:
            return {
                "success": True,
                "already_inactive": True,
                "message": f"Lobe '{lobe_name}' is not active",
                "active_lobes": active_lobes,
            }

        # Remove from active lobes
        active_lobes.remove(lobe_name)
        memory_cortex["active_lobes"] = active_lobes
        ledger["memory_cortex"] = memory_cortex

        # Update ledger
        success = ledger_service.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "lobe_name": lobe_name,
                "deactivated": True,
                "active_lobes": active_lobes,
                "total_active": len(active_lobes),
                "message": f"Lobe '{lobe_name}' deactivated successfully",
            }
        else:
            return {"success": False, "error": "Failed to update ledger"}

    def get_checkpoint_tree(self, lobe_name: str) -> Dict[str, Any]:
        """
        Extract checkpoint tree from a lobe.

        Args:
            lobe_name: Name of the lobe

        Returns:
            Dictionary with checkpoint tree
        """
        content = self.repository.read_lobe(lobe_name)

        if content is None:
            return {
                "success": False,
                "error": f"Lobe '{lobe_name}' not found",
                "lobe_name": lobe_name,
                "exists": False,
            }

        # Extract checkpoints from markdown format
        checkpoints = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            # Look for checklist items
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                checkpoints.append(line)
            # Also look for numbered checkpoints
            elif re.match(r"^\d+\.\s+\[[ x]\]", line):
                checkpoints.append(line)
            # Look for checkpoint markers
            elif "CP-" in line.upper():
                checkpoints.append(line)

        # Extract hierarchy (simplified)
        checkpoint_tree = []
        current_parent = None

        for checkpoint in checkpoints:
            # Simple hierarchy detection based on indentation
            if checkpoint.startswith("  ") or checkpoint.startswith("\t"):
                # Child checkpoint
                if current_parent is not None:
                    checkpoint_tree.append(
                        {
                            "checkpoint": checkpoint.strip(),
                            "type": "child",
                            "parent": current_parent,
                        }
                    )
            else:
                # Parent checkpoint
                current_parent = checkpoint.strip()
                checkpoint_tree.append({"checkpoint": current_parent, "type": "parent"})

        return {
            "success": True,
            "lobe_name": lobe_name,
            "exists": True,
            "checkpoints": checkpoints,
            "checkpoint_tree": checkpoint_tree,
            "total_checkpoints": len(checkpoints),
            "has_checkpoints": len(checkpoints) > 0,
        }

    def search_lobes_advanced(
        self,
        query: str,
        module: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Advanced search across lobes with metadata filtering.

        Args:
            query: Full-text search query
            module: Filter by module name
            status: Filter by status
            tags: Filter by tags (list)
            limit: Maximum number of results

        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Use LobeIndex for advanced search
            index_results = self.index.search_lobes(
                query=query, module=module, status=status, tags=tags, limit=limit
            )

            # Transform results to consistent format
            results = []
            for item in index_results:
                results.append(
                    {
                        "lobe_name": item.get("lobe_name", item.get("lobe_id", "")),
                        "module": item.get("module", ""),
                        "status": item.get("status", ""),
                        "tags": item.get("tags", []),
                        "relevance": item.get("relevance", 1.0),
                        "excerpt": item.get("content", "")[:200] + "..."
                        if item.get("content")
                        else "",
                        "title": item.get("title", ""),
                    }
                )

            return {
                "success": True,
                "query": query,
                "filters": {
                    "module": module,
                    "status": status,
                    "tags": tags,
                },
                "limit": limit,
                "total_results": len(results),
                "results": results,
            }
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Advanced search failed: {e}")
            return {
                "success": False,
                "error": f"Search failed: {e}",
                "query": query,
                "filters": {"module": module, "status": status, "tags": tags},
            }


# Singleton instance for convenience
_default_lobe_service = None


def get_lobe_service(
    repository: Optional[LobeRepository] = None,
    index: Optional[LobeIndexService] = None,
) -> LobeService:
    """
    Get lobe service instance (singleton pattern).

    Args:
        repository: Optional repository implementation
        index: Optional index service implementation

    Returns:
        LobeService instance
    """
    global _default_lobe_service

    if repository is not None or index is not None:
        return LobeService(repository=repository, index=index)

    if _default_lobe_service is None:
        _default_lobe_service = LobeService()

    return _default_lobe_service
