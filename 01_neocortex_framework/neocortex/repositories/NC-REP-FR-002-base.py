# @UBL @UBL @REP-FR | LEXICO: #REPOS
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.501971'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
----"""

#!/usr/bin/env python3
"""
Repository Pattern Base Interfaces for NeoCortex

Defines abstract interfaces for storage operations, enabling multiple
implementations (filesystem, database, hub, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any


class Repository(ABC):
    """Base repository interface for NeoCortex storage operations."""

    @abstractmethod
    def read(self, identifier: str) -> Any:
        """Read data by identifier."""
        pass

    @abstractmethod
    def write(self, identifier: str, data: Any) -> bool:
        """Write data by identifier."""
        pass

    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if identifier exists."""
        pass

    @abstractmethod
    def list(self) -> list[str]:
        """List all available identifiers."""
        pass


class CortexRepository(Repository):
    """Repository interface for Cortex operations."""

    @abstractmethod
    def read_cortex(self) -> str:
        """Read the entire cortex content."""
        pass

    @abstractmethod
    def write_cortex(self, content: str) -> bool:
        """Write content to cortex."""
        pass

    @abstractmethod
    def get_aliases(self) -> dict[str, str]:
        """Extract and return all aliases from cortex."""
        pass

    @abstractmethod
    def get_workflows(self) -> list[dict[str, Any]]:
        """Extract and return all workflows from cortex."""
        pass


class LedgerRepository(Repository):
    """Repository interface for Ledger operations."""

    @abstractmethod
    def read_ledger(self) -> dict[str, Any]:
        """Read the entire ledger content."""
        pass

    @abstractmethod
    def write_ledger(self, data: dict[str, Any]) -> bool:
        """Write data to ledger."""
        pass

    @abstractmethod
    def update_ledger_section(self, section: str, data: dict[str, Any]) -> bool:
        """Update a specific section of the ledger."""
        pass

    @abstractmethod
    def add_changelog_entry(self, change: str, impact: str) -> bool:
        """Add an entry to the changelog."""
        pass

    @abstractmethod
    def get_system_constraints(self) -> dict[str, Any]:
        """Get system constraints from ledger."""
        pass


class ProfileRepository(Repository):
    """Repository interface for Profile operations."""

    @abstractmethod
    def read_profile(self, profile_id: str) -> dict[str, Any]:
        """Read a specific profile."""
        pass

    @abstractmethod
    def write_profile(self, profile_id: str, data: dict[str, Any]) -> bool:
        """Write or update a profile."""
        pass

    @abstractmethod
    def list_profiles(self) -> list[str]:
        """List all available profile IDs."""
        pass

    @abstractmethod
    def get_profile_access_level(self, profile_id: str) -> str:
        """Get access level for a profile (developer/manager/owner)."""
        pass


class LobeRepository(Repository):
    """Repository interface for Lobe operations."""

    @abstractmethod
    def read_lobe(self, lobe_name: str) -> str | None:
        """Read a specific lobe content."""
        pass

    @abstractmethod
    def write_lobe(self, lobe_name: str, content: str) -> bool:
        """Write content to a lobe."""
        pass

    @abstractmethod
    def list_lobes(self) -> list[str]:
        """List all available lobe names."""
        pass

    @abstractmethod
    def lobe_exists(self, lobe_name: str) -> bool:
        """Check if a lobe exists."""
        pass
