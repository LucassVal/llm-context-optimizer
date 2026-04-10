#!/usr/bin/env python3
"""
Consolidation Service - Business logic for semantic consolidation.

This service encapsulates business logic for consolidation operations,
using repository interfaces for storage abstraction.
"""

import json
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository, CortexRepository


class ConsolidationService:
    """Service for consolidation business logic."""

    def __init__(
        self,
        ledger_repository: Optional[LedgerRepository] = None,
        cortex_repository: Optional[CortexRepository] = None,
    ):
        """
        Initialize consolidation service.

        Args:
            ledger_repository: Ledger repository implementation
            cortex_repository: Cortex repository implementation
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

    def _ensure_consolidation_structure(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure consolidation structure exists in memory_cortex."""
        memory_cortex = ledger.get("memory_cortex", {})
        if "consolidation_sessions" not in memory_cortex:
            memory_cortex["consolidation_sessions"] = []
            ledger["memory_cortex"] = memory_cortex
        return ledger

    def summarize_session(
        self, session_id: str, summary: str = "", metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Summarize a session into concise rules.

        Args:
            session_id: Session identifier
            summary: Summary text (if empty, auto-generated)
            metadata: Optional session metadata

        Returns:
            Operation result dictionary
        """
        if not session_id:
            return {"success": False, "error": "session_id is required"}

        ledger = self.ledger_repository.read_ledger()
        ledger = self._ensure_consolidation_structure(ledger)

        consolidation_sessions = ledger["memory_cortex"]["consolidation_sessions"]

        # Create new session
        new_session = {
            "id": session_id,
            "summary": summary if summary else "Session automatically consolidated",
            "created_at": "auto_generated",
            "metadata": metadata or {},
            "status": "summarized",
        }

        # Add to list of sessions
        consolidation_sessions.append(new_session)
        ledger["memory_cortex"]["consolidation_sessions"] = consolidation_sessions

        self.ledger_repository.write_ledger(ledger)

        return {
            "success": True,
            "session": new_session,
            "message": f"Session '{session_id}' summarized and stored",
        }

    def merge_learnings(self) -> Dict[str, Any]:
        """
        Merge learnings from multiple summarized sessions.

        Returns:
            Operation result dictionary
        """
        ledger = self.ledger_repository.read_ledger()
        ledger = self._ensure_consolidation_structure(ledger)

        consolidation_sessions = ledger["memory_cortex"]["consolidation_sessions"]

        # Find summarized sessions
        summarized = [
            s for s in consolidation_sessions if s.get("status") == "summarized"
        ]

        if len(summarized) < 2:
            return {
                "success": False,
                "error": "At least 2 summarized sessions required for merge",
            }

        # Simple merge: combine summaries
        combined_summary = "\n".join([s.get("summary", "") for s in summarized])
        merged_id = f"merged_{len(summarized)}_sessions"

        merged_session = {
            "id": merged_id,
            "summary": combined_summary,
            "created_at": "auto_generated",
            "source_sessions": [s["id"] for s in summarized],
            "status": "merged",
        }

        consolidation_sessions.append(merged_session)
        ledger["memory_cortex"]["consolidation_sessions"] = consolidation_sessions

        self.ledger_repository.write_ledger(ledger)

        return {
            "success": True,
            "merged_session": merged_session,
            "message": f"Learnings from {len(summarized)} sessions merged",
        }

    def promote_to_rule(self, target: str = "") -> Dict[str, Any]:
        """
        Promote an entry from regression buffer to permanent rule.

        Args:
            target: Target entry ID or index (if empty, uses first entry)

        Returns:
            Operation result dictionary
        """
        ledger = self.ledger_repository.read_ledger()

        # Access regression buffer
        hierarchical_validation = ledger.get("hierarchical_validation", {})
        regression_buffer = hierarchical_validation.get("regression_buffer", {})
        failed_attempts = regression_buffer.get("failed_attempts", [])

        if not target and not failed_attempts:
            return {
                "success": False,
                "error": "No entries in Regression Buffer to promote",
            }

        # Find target entry
        target_entry = None
        if not target:
            target_entry = failed_attempts[0] if failed_attempts else None
        else:
            try:
                idx = int(target)
                target_entry = (
                    failed_attempts[idx] if idx < len(failed_attempts) else None
                )
            except ValueError:
                # Search by ID
                target_entry = next(
                    (e for e in failed_attempts if e.get("id") == target), None
                )

        if not target_entry:
            return {"success": False, "error": f"Entry not found: {target}"}

        # Read current cortex
        cortex_content = self.cortex_repository.read_cortex()
        if not cortex_content:
            return {"success": False, "error": "Cortex not found or empty"}

        # Extract rule from entry
        rule_text = target_entry.get("error", target_entry.get("description", ""))
        if not rule_text:
            rule_text = f"Promoted rule from Regression Buffer: {target_entry}"

        # Add rule to cortex (append at the end)
        new_rule = f"\n\n##  Promoted Rule (auto)\n\n{rule_text}\n"
        updated_cortex = cortex_content + new_rule

        # Write updated cortex
        if self.cortex_repository.write_cortex(updated_cortex):
            # Mark entry as promoted in regression buffer
            target_entry["promoted"] = True
            target_entry["promoted_at"] = "auto_generated"
            regression_buffer["failed_attempts"] = failed_attempts
            ledger["hierarchical_validation"]["regression_buffer"] = regression_buffer
            self.ledger_repository.write_ledger(ledger)

            return {
                "success": True,
                "rule_added": new_rule,
                "message": "Rule promoted to cortex successfully",
            }
        else:
            return {"success": False, "error": "Failed to write updated cortex"}

    def list_sessions(self, status_filter: str = "") -> Dict[str, Any]:
        """
        List consolidation sessions with optional filtering.

        Args:
            status_filter: Filter by status (e.g., "summarized", "merged")

        Returns:
            Dictionary with sessions list
        """
        ledger = self.ledger_repository.read_ledger()
        ledger = self._ensure_consolidation_structure(ledger)

        consolidation_sessions = ledger["memory_cortex"]["consolidation_sessions"]

        # Apply filter if specified
        if status_filter:
            filtered = [
                s for s in consolidation_sessions if s.get("status") == status_filter
            ]
        else:
            filtered = consolidation_sessions

        # Calculate statistics
        status_counts = {}
        for session in consolidation_sessions:
            status = session.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "success": True,
            "sessions": filtered,
            "total_sessions": len(consolidation_sessions),
            "filtered_count": len(filtered),
            "status_counts": status_counts,
        }

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get a specific consolidation session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session details
        """
        ledger = self.ledger_repository.read_ledger()
        ledger = self._ensure_consolidation_structure(ledger)

        consolidation_sessions = ledger["memory_cortex"]["consolidation_sessions"]

        session = next(
            (s for s in consolidation_sessions if s.get("id") == session_id), None
        )

        if not session:
            return {"success": False, "error": f"Session not found: {session_id}"}

        # Find related sessions (by source_sessions or similar IDs)
        related = []
        for s in consolidation_sessions:
            if s.get("id") != session_id:
                # Check if this session references the target session
                source_sessions = s.get("source_sessions", [])
                if session_id in source_sessions:
                    related.append(s)

        return {
            "success": True,
            "session": session,
            "related_sessions": related,
            "related_count": len(related),
        }


# Singleton instance for convenience
_default_consolidation_service = None


def get_consolidation_service(
    ledger_repository: Optional[LedgerRepository] = None,
    cortex_repository: Optional[CortexRepository] = None,
) -> ConsolidationService:
    """
    Get consolidation service instance (singleton pattern).

    Args:
        ledger_repository: Optional ledger repository implementation
        cortex_repository: Optional cortex repository implementation

    Returns:
        ConsolidationService instance
    """
    global _default_consolidation_service

    if ledger_repository is not None or cortex_repository is not None:
        return ConsolidationService(ledger_repository, cortex_repository)

    if _default_consolidation_service is None:
        _default_consolidation_service = ConsolidationService()

    return _default_consolidation_service
