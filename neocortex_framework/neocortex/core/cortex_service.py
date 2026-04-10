#!/usr/bin/env python3
"""
Cortex Service - Business logic for cortex operations.

This service encapsulates business logic for cortex operations,
using repository interfaces for storage abstraction.
"""

import re
from typing import Dict, Any, List, Optional
from ..repositories import CortexRepository


class CortexService:
    """Service for cortex-related business logic."""

    def __init__(self, repository: Optional[CortexRepository] = None):
        """
        Initialize cortex service.

        Args:
            repository: Cortex repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemCortexRepository.
        """
        if repository is None:
            from ..repositories import FileSystemCortexRepository

            self.repository = FileSystemCortexRepository()
        else:
            self.repository = repository

    def get_full_cortex(self) -> Dict[str, Any]:
        """
        Get full cortex content with metadata.

        Returns:
            Dictionary with cortex content and metadata
        """
        content = self.repository.read_cortex()
        aliases = self.repository.get_aliases()
        workflows = self.repository.get_workflows()

        return {
            "content": content,
            "metadata": {
                "aliases_count": len(aliases),
                "workflows_count": len(workflows),
                "size_chars": len(content),
                "lines": content.count("\n") + 1,
            },
            "aliases": aliases,
            "workflows": workflows,
        }

    def get_cortex_section(self, section: str) -> Dict[str, Any]:
        """
        Get a specific section from cortex.

        Args:
            section: Section name (e.g., "aliases", "workflows", "patterns")

        Returns:
            Dictionary with section content
        """
        content = self.repository.read_cortex()

        # Try to find section by markdown header
        section_pattern = rf"^## {re.escape(section)}(?:$|\s.*?$)(.*?)(?=^## |\Z)"
        match = re.search(
            section_pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE
        )

        if match:
            section_content = match.group(1).strip()
            return {"section": section, "content": section_content, "found": True}

        # Fallback: look for any mention of section
        lines = content.split("\n")
        section_lines = []
        in_section = False

        for line in lines:
            if line.strip().lower().startswith(f"## {section.lower()}"):
                in_section = True
                continue
            if in_section and line.strip().startswith("##"):
                break
            if in_section:
                section_lines.append(line)

        if section_lines:
            return {
                "section": section,
                "content": "\n".join(section_lines).strip(),
                "found": True,
                "note": "Section found by loose matching",
            }

        return {
            "section": section,
            "content": "",
            "found": False,
            "error": f"Section '{section}' not found in cortex",
        }

    def get_aliases(self) -> Dict[str, str]:
        """
        Get all aliases from cortex.

        Returns:
            Dictionary mapping alias names to values
        """
        return self.repository.get_aliases()

    def get_workflows(self) -> List[Dict[str, Any]]:
        """
        Get all workflows from cortex.

        Returns:
            List of workflow dictionaries
        """
        return self.repository.get_workflows()

    def validate_alias(self, alias: str) -> Dict[str, Any]:
        """
        Validate if an alias exists and is correctly defined.

        Args:
            alias: Alias name (with or without $ prefix)

        Returns:
            Validation result dictionary
        """
        # Ensure alias has $ prefix
        if not alias.startswith("$"):
            alias = f"${alias}"

        aliases = self.repository.get_aliases()

        if alias in aliases:
            return {
                "alias": alias,
                "exists": True,
                "value": aliases[alias],
                "valid": True,
            }

        # Check if alias exists without $ prefix
        alias_no_dollar = alias[1:] if alias.startswith("$") else alias
        for existing_alias, value in aliases.items():
            existing_no_dollar = (
                existing_alias[1:] if existing_alias.startswith("$") else existing_alias
            )
            if existing_no_dollar == alias_no_dollar:
                return {
                    "alias": alias,
                    "exists": True,
                    "actual_alias": existing_alias,
                    "value": value,
                    "valid": True,
                    "note": "Alias found with different prefix",
                }

        return {
            "alias": alias,
            "exists": False,
            "valid": False,
            "error": f"Alias '{alias}' not found in cortex",
        }

    def search_cortex(self, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for text in cortex content.

        Args:
            query: Text to search for
            case_sensitive: Whether search is case-sensitive

        Returns:
            Search results dictionary
        """
        content = self.repository.read_cortex()

        if case_sensitive:
            matches = [match for match in re.finditer(re.escape(query), content)]
        else:
            matches = [
                match for match in re.finditer(re.escape(query), content, re.IGNORECASE)
            ]

        results = []
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]

            # Add line number
            line_number = content[: match.start()].count("\n") + 1

            results.append(
                {
                    "position": match.start(),
                    "line": line_number,
                    "context": context,
                    "match": match.group(),
                }
            )

        return {
            "query": query,
            "case_sensitive": case_sensitive,
            "total_matches": len(matches),
            "results": results,
        }

    def update_cortex(self, content: str) -> Dict[str, Any]:
        """
        Update cortex content with validation.

        Args:
            content: New cortex content

        Returns:
            Update result dictionary
        """
        # Basic validation
        if not content.strip():
            return {"success": False, "error": "Cortex content cannot be empty"}

        # Check for required sections
        required_sections = ["# NeoCortex Cortex"]
        missing_sections = []

        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            return {
                "success": False,
                "error": f"Missing required sections: {missing_sections}",
                "missing_sections": missing_sections,
            }

        # Write to repository
        success = self.repository.write_cortex(content)

        if success:
            return {
                "success": True,
                "message": "Cortex updated successfully",
                "size_chars": len(content),
                "lines": content.count("\n") + 1,
            }
        else:
            return {"success": False, "error": "Failed to write cortex to storage"}


# Singleton instance for convenience
_default_cortex_service = None


def get_cortex_service(repository: Optional[CortexRepository] = None) -> CortexService:
    """
    Get cortex service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        CortexService instance
    """
    global _default_cortex_service

    if repository is not None:
        return CortexService(repository)

    if _default_cortex_service is None:
        _default_cortex_service = CortexService()

    return _default_cortex_service
