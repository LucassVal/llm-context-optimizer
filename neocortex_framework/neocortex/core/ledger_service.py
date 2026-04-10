#!/usr/bin/env python3
"""
Ledger Service - Business logic for ledger operations.

This service encapsulates business logic for ledger operations,
using repository interfaces for storage abstraction.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository
from ..schemas import LEDGER_SCHEMA


class LedgerService:
    """Service for ledger-related business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize ledger service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLedgerRepository.
        """
        if repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.repository = FileSystemLedgerRepository()
        else:
            self.repository = repository

    def get_full_ledger(self) -> Dict[str, Any]:
        """
        Get full ledger content.

        Returns:
            Complete ledger dictionary
        """
        return self.repository.read_ledger()

    def get_ledger_section(self, section_path: str) -> Dict[str, Any]:
        """
        Get a specific section from ledger using dot notation.

        Args:
            section_path: Path to section using dot notation (e.g., "system_constraints.max_context_depth")

        Returns:
            Section content dictionary
        """
        ledger = self.repository.read_ledger()

        # Navigate nested sections
        keys = section_path.split(".")
        current = ledger

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return {
                    "section": section_path,
                    "found": False,
                    "error": f"Section '{key}' not found in path '{section_path}'",
                }

        return {"section": section_path, "content": current, "found": True}

    def update_ledger_section(self, section_path: str, data: Any) -> Dict[str, Any]:
        """
        Update a specific section in ledger.

        Args:
            section_path: Path to section using dot notation
            data: New data for the section

        Returns:
            Update result dictionary
        """
        # Validate data structure (simplified validation)
        if not isinstance(data, (dict, list, str, int, float, bool, type(None))):
            return {
                "success": False,
                "error": f"Invalid data type: {type(data)}. Must be JSON-serializable.",
            }

        # Update via repository
        success = self.repository.update_ledger_section(section_path, data)

        if success:
            return {
                "success": True,
                "message": f"Section '{section_path}' updated successfully",
                "section": section_path,
                "data": data,
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update section '{section_path}'",
            }

    def add_changelog_entry(
        self, change: str, impact: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add an entry to the changelog.

        Args:
            change: Description of the change
            impact: Description of the impact
            metadata: Optional additional metadata

        Returns:
            Operation result dictionary
        """
        if not change.strip():
            return {"success": False, "error": "Change description cannot be empty"}

        if not impact.strip():
            return {"success": False, "error": "Impact description cannot be empty"}

        success = self.repository.add_changelog_entry(change, impact)

        if success:
            entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "change": change,
                "impact": impact,
            }

            if metadata:
                entry["metadata"] = metadata

            return {
                "success": True,
                "message": "Changelog entry added successfully",
                "entry": entry,
            }
        else:
            return {"success": False, "error": "Failed to add changelog entry"}

    def get_system_constraints(self) -> Dict[str, Any]:
        """
        Get system constraints from ledger.

        Returns:
            System constraints dictionary
        """
        return self.repository.get_system_constraints()

    def validate_ledger(self) -> Dict[str, Any]:
        """
        Validate ledger structure against schema.

        Returns:
            Validation results dictionary
        """
        ledger = self.repository.read_ledger()

        # Basic validation
        if not ledger:
            return {"valid": False, "errors": ["Ledger is empty"]}

        required_fields = [
            "neocortex_version",
            "system_type",
            "architecture",
            "system_constraints",
        ]

        missing_fields = []
        for field in required_fields:
            if field not in ledger:
                missing_fields.append(field)

        if missing_fields:
            return {
                "valid": False,
                "errors": [f"Missing required fields: {missing_fields}"],
            }

        # If schema is available, validate against it
        if LEDGER_SCHEMA:
            try:
                import jsonschema

                jsonschema.validate(instance=ledger, schema=LEDGER_SCHEMA)
                schema_valid = True
                schema_errors = []
            except ImportError:
                schema_valid = True  # Skip if jsonschema not installed
                schema_errors = [
                    "jsonschema package not installed - schema validation skipped"
                ]
            except jsonschema.ValidationError as e:
                schema_valid = False
                schema_errors = [str(e)]
        else:
            schema_valid = True
            schema_errors = ["LEDGER_SCHEMA not loaded - schema validation skipped"]

        # Check data integrity
        constraints = ledger.get("system_constraints", {})
        integrity_checks = []

        if "max_context_depth" in constraints:
            depth = constraints["max_context_depth"]
            if not isinstance(depth, int) or depth <= 0:
                integrity_checks.append(f"Invalid max_context_depth: {depth}")

        if "hot_context_limit" in constraints:
            limit = constraints["hot_context_limit"]
            if not isinstance(limit, int) or limit <= 0:
                integrity_checks.append(f"Invalid hot_context_limit: {limit}")

        all_valid = schema_valid and not integrity_checks

        return {
            "valid": all_valid,
            "schema_valid": schema_valid,
            "schema_errors": schema_errors,
            "integrity_checks": integrity_checks,
            "missing_fields": missing_fields,
            "ledger_size": len(json.dumps(ledger)),
            "sections_count": len(ledger),
        }

    def get_session_metrics(self) -> Dict[str, Any]:
        """
        Get session metrics from ledger.

        Returns:
            Session metrics dictionary
        """
        ledger = self.repository.read_ledger()
        metrics = ledger.get("session_metrics", {})

        # Calculate additional derived metrics
        total_interactions = metrics.get("total_interactions", 0)
        compactions = metrics.get("compactions_executed", 0)
        warnings = metrics.get("token_budget_warnings", 0)

        compaction_rate = (
            compactions / total_interactions if total_interactions > 0 else 0
        )
        warning_rate = warnings / total_interactions if total_interactions > 0 else 0

        return {
            **metrics,
            "derived_metrics": {
                "compaction_rate": round(compaction_rate, 3),
                "warning_rate": round(warning_rate, 3),
                "interactions_per_compaction": total_interactions / compactions
                if compactions > 0
                else 0,
                "health_score": 100 - (warning_rate * 100),
            },
        }

    def update_session_metrics(
        self, interaction_type: str = "generic", tokens_used: int = 0
    ) -> Dict[str, Any]:
        """
        Update session metrics after an interaction.

        Args:
            interaction_type: Type of interaction (query, tool_usage, etc.)
            tokens_used: Number of tokens used in interaction

        Returns:
            Update result dictionary
        """
        ledger = self.repository.read_ledger()

        # Update metrics
        if "session_metrics" not in ledger:
            ledger["session_metrics"] = {
                "total_interactions": 0,
                "compactions_executed": 0,
                "token_budget_warnings": 0,
            }

        metrics = ledger["session_metrics"]
        metrics["total_interactions"] = metrics.get("total_interactions", 0) + 1

        # Track interaction type if not already present
        if "interaction_types" not in metrics:
            metrics["interaction_types"] = {}

        metrics["interaction_types"][interaction_type] = (
            metrics["interaction_types"].get(interaction_type, 0) + 1
        )

        # Track token usage
        if "total_tokens_used" not in metrics:
            metrics["total_tokens_used"] = 0

        metrics["total_tokens_used"] += tokens_used

        # Check for token budget warnings
        constraints = ledger.get("system_constraints", {})
        max_tokens = constraints.get("max_json_size_tokens", 8000)
        warning_threshold = constraints.get("warning_threshold_tokens", 6000)

        if tokens_used > warning_threshold:
            metrics["token_budget_warnings"] = (
                metrics.get("token_budget_warnings", 0) + 1
            )

            # Add warning to agent_session
            if "agent_session" not in ledger:
                ledger["agent_session"] = {}

            if "token_budget_warnings" not in ledger["agent_session"]:
                ledger["agent_session"]["token_budget_warnings"] = []

            warning_msg = f"Interaction used {tokens_used} tokens (threshold: {warning_threshold})"
            ledger["agent_session"]["token_budget_warnings"].append(
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "message": warning_msg,
                    "tokens_used": tokens_used,
                }
            )

        # Write updated ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "message": "Session metrics updated",
                "metrics": metrics,
            }
        else:
            return {"success": False, "error": "Failed to update session metrics"}


# Singleton instance for convenience
_default_ledger_service = None


def get_ledger_service(repository: Optional[LedgerRepository] = None) -> LedgerService:
    """
    Get ledger service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        LedgerService instance
    """
    global _default_ledger_service

    if repository is not None:
        return LedgerService(repository)

    if _default_ledger_service is None:
        _default_ledger_service = LedgerService()

    return _default_ledger_service
