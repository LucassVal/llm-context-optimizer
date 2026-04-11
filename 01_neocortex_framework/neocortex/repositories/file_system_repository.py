#!/usr/bin/env python3
"""
File System Repository Implementation

Concrete implementation of repository interfaces using local filesystem.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base import CortexRepository, LedgerRepository, ProfileRepository, LobeRepository
from ..core.file_utils import (
    read_cortex,
    write_cortex,
    read_ledger,
    write_ledger,
    find_lobes,
    get_lobe_content,
    get_project_root,
    path_exists,
    read_json_file,
    write_json_file,
)

logger = logging.getLogger(__name__)


class FileSystemCortexRepository(CortexRepository):
    """Filesystem implementation for Cortex repository."""

    def read(self, identifier: str) -> Any:
        """Read cortex by identifier (currently only 'cortex' supported)."""
        if identifier != "cortex":
            raise ValueError(f"Unknown cortex identifier: {identifier}")
        return self.read_cortex()

    def write(self, identifier: str, data: Any) -> bool:
        """Write cortex by identifier."""
        if identifier != "cortex":
            raise ValueError(f"Unknown cortex identifier: {identifier}")
        if not isinstance(data, str):
            raise TypeError("Cortex data must be string")
        return self.write_cortex(data)

    def exists(self, identifier: str) -> bool:
        """Check if cortex exists."""
        if identifier != "cortex":
            return False
        return path_exists(
            "DIR-CORE-FR-001-core-central/.agents/rules/NC-CTX-FR-001-cortex-central.mdc"
        )

    def list(self) -> List[str]:
        """List available cortex identifiers (only 'cortex')."""
        return ["cortex"] if self.exists("cortex") else []

    def read_cortex(self) -> str:
        """Read the entire cortex content."""
        return read_cortex()

    def write_cortex(self, content: str) -> bool:
        """Write content to cortex."""
        return write_cortex(content)

    def get_aliases(self) -> Dict[str, str]:
        """Extract and return all aliases from cortex."""
        content = self.read_cortex()
        aliases = {}

        # Find Workspace Map section
        lines = content.split("\n")
        in_section = False
        header_found = False
        separator_found = False

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Look for "## 📍 Workspace Map" or "## Workspace Map"
            if line_stripped.startswith("##") and "Workspace Map" in line_stripped:
                in_section = True
                continue

            if not in_section:
                continue

            # Check for header row (contains "File/Dir" and "Alias")
            if (
                in_section
                and not header_found
                and "|" in line_stripped
                and "File/Dir" in line_stripped
                and "Alias" in line_stripped
            ):
                header_found = True
                continue

            # Check for separator row (contains "|---" or ":---")
            if (
                in_section
                and header_found
                and not separator_found
                and "|" in line_stripped
                and ("---" in line_stripped or ":---" in line_stripped)
            ):
                separator_found = True
                continue

            # If we're past separator, parse data rows until empty line or new section
            if in_section and header_found and separator_found:
                # End of table if line doesn't contain '|' or starts with '##'
                if not line_stripped or line_stripped.startswith("##"):
                    break
                if "|" not in line_stripped:
                    continue

                # Parse markdown table row: remove leading/trailing '|' and split
                cells = [cell.strip() for cell in line_stripped.strip("|").split("|")]
                if len(cells) >= 2:
                    # Remove backticks if present
                    path = cells[0].strip(" `")
                    alias = cells[1].strip(" `")
                    aliases[alias] = path

        # Fallback to regex extraction if no aliases found
        if not aliases:
            alias_pattern = r'\$(\w+)\s*=\s*[\'"](.+?)[\'"]'
            matches = re.findall(alias_pattern, content, re.MULTILINE | re.DOTALL)
            for alias_name, alias_value in matches:
                aliases[alias_name] = alias_value

        return aliases

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Extract and return all workflows from cortex."""
        content = self.read_cortex()
        workflows = []
        lines = content.split("\n")
        in_workflows = False
        current_workflow = None

        for line in lines:
            stripped = line.strip()
            # Start of workflows section
            if stripped.startswith("##") and "Workflows" in stripped:
                in_workflows = True
                continue
            # If we're in workflows and encounter another top-level heading, exit
            if (
                in_workflows
                and stripped.startswith("## ")
                and not stripped.startswith("###")
            ):
                # This is a new top-level section, stop processing
                break
            # Subsection heading (workflow)
            if in_workflows and stripped.startswith("### ") and "Workflow:" in stripped:
                if current_workflow:
                    workflows.append(current_workflow)
                # Extract workflow name (remove "### " and "Workflow:" prefix)
                name = stripped.replace("### ", "", 1).strip()
                # Remove emoji if present
                if "🔍" in name:
                    name = name.replace("🔍", "").strip()
                if "🐛" in name:
                    name = name.replace("🐛", "").strip()
                if "🏁" in name:
                    name = name.replace("🏁", "").strip()
                current_workflow = {"name": name, "description": "", "steps": []}
                continue
            # If we're in a workflow and line is a numbered step
            if (
                in_workflows
                and current_workflow
                and stripped
                and stripped[0].isdigit()
                and ". " in stripped
            ):
                # Remove bold markers ** if present
                step_text = stripped
                if "**" in step_text:
                    step_text = step_text.replace("**", "")
                # Split step number and description
                parts = step_text.split(". ", 1)
                step_num = parts[0].strip()
                step_desc = parts[1].strip() if len(parts) > 1 else ""
                current_workflow["steps"].append(
                    {"step": step_num, "description": step_desc}
                )
                continue
            # Capture description (lines after workflow title before first step)
            if (
                in_workflows
                and current_workflow
                and not current_workflow["steps"]
                and stripped
                and not stripped.startswith(">")
                and not stripped.startswith("#")
            ):
                if current_workflow["description"]:
                    current_workflow["description"] += " " + stripped
                else:
                    current_workflow["description"] = stripped

        # Add last workflow
        if current_workflow:
            workflows.append(current_workflow)

        return workflows


class FileSystemLedgerRepository(LedgerRepository):
    """Filesystem implementation for Ledger repository."""

    def read(self, identifier: str) -> Any:
        """Read ledger by identifier (currently only 'ledger' supported)."""
        if identifier != "ledger":
            raise ValueError(f"Unknown ledger identifier: {identifier}")
        return self.read_ledger()

    def write(self, identifier: str, data: Any) -> bool:
        """Write ledger by identifier."""
        if identifier != "ledger":
            raise ValueError(f"Unknown ledger identifier: {identifier}")
        if not isinstance(data, dict):
            raise TypeError("Ledger data must be dictionary")
        return self.write_ledger(data)

    def exists(self, identifier: str) -> bool:
        """Check if ledger exists."""
        if identifier != "ledger":
            return False
        return path_exists(
            "DIR-CORE-FR-001-core-central/NC-LED-FR-001-framework-ledger.json"
        )

    def list(self) -> List[str]:
        """List available ledger identifiers (only 'ledger')."""
        return ["ledger"] if self.exists("ledger") else []

    def read_ledger(self) -> Dict[str, Any]:
        """Read the entire ledger content."""
        return read_ledger()

    def write_ledger(self, data: Dict[str, Any]) -> bool:
        """Write data to ledger."""
        return write_ledger(data)

    def update_ledger_section(self, section: str, data: Dict[str, Any]) -> bool:
        """Update a specific section of the ledger."""
        ledger = self.read_ledger()

        # Navigate nested sections using dot notation
        keys = section.split(".")
        current = ledger

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = data

        return self.write_ledger(ledger)

    def add_changelog_entry(self, change: str, impact: str) -> bool:
        """Add an entry to the changelog."""
        ledger = self.read_ledger()

        # Ensure changelog structure exists
        if "changelog" not in ledger:
            ledger["changelog"] = {"entries": []}
        elif "entries" not in ledger["changelog"]:
            ledger["changelog"]["entries"] = []

        # Add new entry
        from datetime import datetime

        new_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "change": change,
            "impact": impact,
        }

        ledger["changelog"]["entries"].insert(0, new_entry)  # Add to beginning

        return self.write_ledger(ledger)

    def get_system_constraints(self) -> Dict[str, Any]:
        """Get system constraints from ledger."""
        ledger = self.read_ledger()
        return ledger.get("system_constraints", {})


class FileSystemProfileRepository(ProfileRepository):
    """Filesystem implementation for Profile repository."""

    def __init__(self):
        self.profiles_dir = (
            get_project_root() / "DIR-PRF-FR-001-profiles-main" / "users"
        )

    def read(self, identifier: str) -> Any:
        """Read profile by ID."""
        return self.read_profile(identifier)

    def write(self, identifier: str, data: Any) -> bool:
        """Write profile by ID."""
        if not isinstance(data, dict):
            raise TypeError("Profile data must be dictionary")
        return self.write_profile(identifier, data)

    def exists(self, identifier: str) -> bool:
        """Check if profile exists."""
        profile_path = self.profiles_dir / f"{identifier}.json"
        return profile_path.exists()

    def list(self) -> List[str]:
        """List all available profile IDs."""
        if not self.profiles_dir.exists():
            return []

        profiles = []
        for file in self.profiles_dir.glob("*.json"):
            profiles.append(file.stem)

        return profiles

    def read_profile(self, profile_id: str) -> Dict[str, Any]:
        """Read a specific profile."""
        profile_path = self.profiles_dir / f"{profile_id}.json"
        if not profile_path.exists():
            return {}

        return read_json_file(profile_path)

    def write_profile(self, profile_id: str, data: Dict[str, Any]) -> bool:
        """Write or update a profile."""
        profile_path = self.profiles_dir / f"{profile_id}.json"

        # Ensure profiles directory exists
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        return write_json_file(profile_path, data)

    def list_profiles(self) -> List[str]:
        """List all available profile IDs."""
        return self.list()

    def get_profile_access_level(self, profile_id: str) -> str:
        """Get access level for a profile (developer/manager/owner)."""
        profile = self.read_profile(profile_id)
        return profile.get("access_level", "developer")


class FileSystemLobeRepository(LobeRepository):
    """Filesystem implementation for Lobe repository."""

    def __init__(self):
        self.lobes_dir = (
            get_project_root() / "DIR-CORE-FR-001-core-central" / ".agents" / "rules"
        )

    def read(self, identifier: str) -> Any:
        """Read lobe by name."""
        return self.read_lobe(identifier)

    def write(self, identifier: str, data: Any) -> bool:
        """Write lobe by name."""
        if not isinstance(data, str):
            raise TypeError("Lobe data must be string")
        return self.write_lobe(identifier, data)

    def exists(self, identifier: str) -> bool:
        """Check if lobe exists."""
        return self.lobe_exists(identifier)

    def list(self) -> List[str]:
        """List all available lobe names."""
        return self.list_lobes()

    def read_lobe(self, lobe_name: str) -> Optional[str]:
        """Read a specific lobe content."""
        # Use existing utility function
        return get_lobe_content(lobe_name)

    def write_lobe(self, lobe_name: str, content: str) -> bool:
        """Write content to a lobe."""
        lobe_path = self.lobes_dir / lobe_name

        # Ensure directory exists
        self.lobes_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(lobe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing lobe {lobe_name}: {e}")
            return False

    def list_lobes(self) -> List[str]:
        """List all available lobe names."""
        # Use existing utility function
        return find_lobes()

    def lobe_exists(self, lobe_name: str) -> bool:
        """Check if a lobe exists."""
        lobe_path = self.lobes_dir / lobe_name
        return lobe_path.exists()


class FileSystemRepositoryFactory:
    """Factory for creating filesystem repository instances."""

    @staticmethod
    def create_cortex_repository() -> CortexRepository:
        return FileSystemCortexRepository()

    @staticmethod
    def create_ledger_repository() -> LedgerRepository:
        return FileSystemLedgerRepository()

    @staticmethod
    def create_profile_repository() -> ProfileRepository:
        return FileSystemProfileRepository()

    @staticmethod
    def create_lobe_repository() -> LobeRepository:
        return FileSystemLobeRepository()
