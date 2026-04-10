#!/usr/bin/env python3
"""
Regression Service - Business logic for regression buffer and STEP 0 operations.

This service encapsulates business logic for regression buffer operations,
using repository interfaces for storage abstraction.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class RegressionService:
    """Service for regression buffer and STEP 0 business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize regression service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLedgerRepository.
        """
        if repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.repository = FileSystemLedgerRepository()
        else:
            self.repository = repository

    def check_similar_errors(self, error: str) -> Dict[str, Any]:
        """
        Check for similar errors in regression buffer.

        Args:
            error: Error message to check

        Returns:
            Dictionary with similar errors and metadata
        """
        ledger = self.repository.read_ledger()

        # Get regression buffer from hierarchical_validation
        hierarchical_validation = ledger.get("hierarchical_validation", {})
        regression_buffer = hierarchical_validation.get("regression_buffer", {})
        failed_attempts = regression_buffer.get("failed_attempts", [])

        if not error:
            return {"success": True, "similar_errors": [], "count": 0, "warning": False}

        # Simple similarity check (contains error string)
        similar = [
            entry
            for entry in failed_attempts
            if error.lower() in entry.get("error", "").lower()
        ]

        return {
            "success": True,
            "similar_errors": similar,
            "count": len(similar),
            "warning": len(similar) > 0,
            "total_entries": len(failed_attempts),
        }

    def add_regression_entry(
        self, error: str, attempt: str, lesson: str
    ) -> Dict[str, Any]:
        """
        Add a new entry to regression buffer.

        Args:
            error: Error message
            attempt: Attempted solution
            lesson: Lesson learned

        Returns:
            Dictionary with added entry and metadata
        """
        if not error or not attempt or not lesson:
            return {"success": False, "error": "error, attempt and lesson are required"}

        ledger = self.repository.read_ledger()

        # Ensure hierarchical_validation structure exists
        if "hierarchical_validation" not in ledger:
            ledger["hierarchical_validation"] = {}

        hierarchical_validation = ledger["hierarchical_validation"]

        if "regression_buffer" not in hierarchical_validation:
            hierarchical_validation["regression_buffer"] = {}

        regression_buffer = hierarchical_validation["regression_buffer"]

        if "failed_attempts" not in regression_buffer:
            regression_buffer["failed_attempts"] = []

        # Create new entry
        new_entry = {
            "error": error,
            "attempt": attempt,
            "lesson": lesson,
            "timestamp": datetime.now().isoformat(),
            "source": "regression_tool",
        }

        # Add to buffer
        regression_buffer["failed_attempts"].append(new_entry)

        # Update ledger
        hierarchical_validation["regression_buffer"] = regression_buffer
        ledger["hierarchical_validation"] = hierarchical_validation

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "entry": new_entry,
                "total_entries": len(regression_buffer["failed_attempts"]),
                "message": "Regression entry added successfully",
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def list_all_entries(self) -> Dict[str, Any]:
        """
        List all entries in regression buffer.

        Returns:
            Dictionary with all entries and metadata
        """
        ledger = self.repository.read_ledger()

        # Get regression buffer
        hierarchical_validation = ledger.get("hierarchical_validation", {})
        regression_buffer = hierarchical_validation.get("regression_buffer", {})
        failed_attempts = regression_buffer.get("failed_attempts", [])

        # Calculate statistics
        total_entries = len(failed_attempts)

        # Group by error patterns (simplified)
        error_patterns = {}
        for entry in failed_attempts:
            error = entry.get("error", "")
            # Simple pattern: first 50 chars
            pattern = error[:50] + "..." if len(error) > 50 else error
            error_patterns[pattern] = error_patterns.get(pattern, 0) + 1

        return {
            "success": True,
            "entries": failed_attempts,
            "total": total_entries,
            "statistics": {
                "total_entries": total_entries,
                "unique_error_patterns": len(error_patterns),
                "error_patterns": error_patterns,
            },
        }

    def clear_regression_buffer(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Clear all entries from regression buffer.

        Args:
            confirm: Must be True to actually clear

        Returns:
            Dictionary with result
        """
        if not confirm:
            return {
                "success": False,
                "error": "Confirmation required. Set confirm=True to clear buffer.",
            }

        ledger = self.repository.read_ledger()

        # Ensure hierarchical_validation structure exists
        if "hierarchical_validation" not in ledger:
            ledger["hierarchical_validation"] = {}

        hierarchical_validation = ledger["hierarchical_validation"]

        if "regression_buffer" not in hierarchical_validation:
            hierarchical_validation["regression_buffer"] = {}

        regression_buffer = hierarchical_validation["regression_buffer"]

        # Save count before clearing
        previous_count = len(regression_buffer.get("failed_attempts", []))

        # Clear buffer
        regression_buffer["failed_attempts"] = []

        # Update ledger
        hierarchical_validation["regression_buffer"] = regression_buffer
        ledger["hierarchical_validation"] = hierarchical_validation

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "cleared_entries": previous_count,
                "message": f"Cleared {previous_count} entries from regression buffer",
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def get_buffer_stats(self) -> Dict[str, Any]:
        """
        Get statistics about regression buffer.

        Returns:
            Dictionary with statistics
        """
        ledger = self.repository.read_ledger()

        # Get regression buffer
        hierarchical_validation = ledger.get("hierarchical_validation", {})
        regression_buffer = hierarchical_validation.get("regression_buffer", {})
        failed_attempts = regression_buffer.get("failed_attempts", [])

        # Calculate various statistics
        total_entries = len(failed_attempts)

        # Entry age analysis (if timestamps exist)
        entries_with_timestamps = []
        for entry in failed_attempts:
            if "timestamp" in entry:
                entries_with_timestamps.append(entry)

        # Error length analysis
        error_lengths = [len(entry.get("error", "")) for entry in failed_attempts]
        avg_error_length = (
            sum(error_lengths) / len(error_lengths) if error_lengths else 0
        )

        # Lesson length analysis
        lesson_lengths = [len(entry.get("lesson", "")) for entry in failed_attempts]
        avg_lesson_length = (
            sum(lesson_lengths) / len(lesson_lengths) if lesson_lengths else 0
        )

        return {
            "success": True,
            "total_entries": total_entries,
            "entries_with_timestamps": len(entries_with_timestamps),
            "average_error_length": round(avg_error_length, 1),
            "average_lesson_length": round(avg_lesson_length, 1),
            "buffer_size_bytes": len(str(failed_attempts)),
        }


# Singleton instance for convenience
_default_regression_service = None


def get_regression_service(
    repository: Optional[LedgerRepository] = None,
) -> RegressionService:
    """
    Get regression service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        RegressionService instance
    """
    global _default_regression_service

    if repository is not None:
        return RegressionService(repository)

    if _default_regression_service is None:
        _default_regression_service = RegressionService()

    return _default_regression_service
