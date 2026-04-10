#!/usr/bin/env python3
"""
Adaptive Knowledge Lifecycle Service - Business logic for knowledge relevance management.

This service encapsulates business logic for adaptive knowledge lifecycle operations,
using repository interfaces for storage abstraction.
"""

from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class AKLService:
    """Service for adaptive knowledge lifecycle business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize AKL service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLedgerRepository.
        """
        if repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.repository = FileSystemLedgerRepository()
        else:
            self.repository = repository

    def _ensure_akl_structure(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure AKL metrics structure exists in memory_cortex."""
        memory_cortex = ledger.get("memory_cortex", {})
        if "akl_metrics" not in memory_cortex:
            memory_cortex["akl_metrics"] = {}
            ledger["memory_cortex"] = memory_cortex
        return ledger

    def assess_importance(self, rule_id: str = "") -> Dict[str, Any]:
        """
        Assess importance of rules based on usage.

        Args:
            rule_id: Specific rule ID to assess. If empty, assesses all rules.

        Returns:
            Assessment result dictionary
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_akl_structure(ledger)

        akl_metrics = ledger["memory_cortex"]["akl_metrics"]

        if not rule_id:
            # Assess importance of all rules with existing metrics
            important_rules = []
            for rule_id, metrics in akl_metrics.items():
                importance = metrics.get("access_count", 0) * 10  # Simple weight
                important_rules.append(
                    {
                        "rule_id": rule_id,
                        "importance_score": importance,
                        "access_count": metrics.get("access_count", 0),
                        "last_accessed": metrics.get("last_accessed", "never"),
                    }
                )

            # Sort by descending importance
            important_rules.sort(key=lambda x: x["importance_score"], reverse=True)

            return {
                "success": True,
                "assessment": important_rules,
                "message": f"Assessed {len(important_rules)} rules",
            }

        # Assess specific rule
        if rule_id not in akl_metrics:
            # Create initial entry
            akl_metrics[rule_id] = {
                "access_count": 0,
                "last_accessed": "never",
                "importance_score": 0,
                "created_at": "auto_generated",
            }

        metrics = akl_metrics[rule_id]
        # Increment access count (simulation)
        metrics["access_count"] = metrics.get("access_count", 0) + 1
        metrics["last_accessed"] = "auto_generated"
        metrics["importance_score"] = metrics["access_count"] * 10

        akl_metrics[rule_id] = metrics
        ledger["memory_cortex"]["akl_metrics"] = akl_metrics
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "rule_id": rule_id,
            "importance_score": metrics["importance_score"],
            "access_count": metrics["access_count"],
            "message": f"Importance of rule '{rule_id}' assessed",
        }

    def decay_knowledge(self) -> Dict[str, Any]:
        """
        Apply decay to unused knowledge.

        Returns:
            Decay operation result dictionary
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_akl_structure(ledger)

        akl_metrics = ledger["memory_cortex"]["akl_metrics"]
        decayed_rules = []

        for rule_id, metrics in akl_metrics.items():
            # Reduce score based on inactivity (simplified)
            old_score = metrics.get("importance_score", 0)
            new_score = max(0, old_score - 5)  # Fixed decay
            metrics["importance_score"] = new_score
            akl_metrics[rule_id] = metrics

            if new_score < old_score:
                decayed_rules.append(
                    {
                        "rule_id": rule_id,
                        "old_score": old_score,
                        "new_score": new_score,
                    }
                )

        ledger["memory_cortex"]["akl_metrics"] = akl_metrics
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "decayed_rules": decayed_rules,
            "count": len(decayed_rules),
            "message": f"Decay applied to {len(decayed_rules)} rules",
        }

    def suggest_cleanup(self, threshold: int = 20) -> Dict[str, Any]:
        """
        Suggest rules for archival based on low importance.

        Args:
            threshold: Importance score threshold below which rules are candidates

        Returns:
            Cleanup suggestions dictionary
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_akl_structure(ledger)

        akl_metrics = ledger["memory_cortex"]["akl_metrics"]
        candidates = []

        for rule_id, metrics in akl_metrics.items():
            score = metrics.get("importance_score", 0)
            if score < threshold:
                candidates.append(
                    {
                        "rule_id": rule_id,
                        "importance_score": score,
                        "access_count": metrics.get("access_count", 0),
                        "last_accessed": metrics.get("last_accessed", "never"),
                        "suggestion": "archive",
                    }
                )

        # Sort by lowest importance
        candidates.sort(key=lambda x: x["importance_score"])

        return {
            "success": True,
            "candidates": candidates,
            "count": len(candidates),
            "threshold": threshold,
            "message": f"{len(candidates)} rules candidate for archival",
        }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive AKL metrics.

        Returns:
            Dictionary with AKL metrics
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_akl_structure(ledger)

        akl_metrics = ledger["memory_cortex"]["akl_metrics"]

        # Calculate statistics
        total_rules = len(akl_metrics)
        if total_rules == 0:
            return {
                "success": True,
                "total_rules": 0,
                "message": "No AKL metrics available",
            }

        total_access_count = sum(m.get("access_count", 0) for m in akl_metrics.values())
        avg_importance = (
            sum(m.get("importance_score", 0) for m in akl_metrics.values())
            / total_rules
        )

        # Categorize by importance level
        high_importance = [
            r for r, m in akl_metrics.items() if m.get("importance_score", 0) >= 50
        ]
        medium_importance = [
            r for r, m in akl_metrics.items() if 20 <= m.get("importance_score", 0) < 50
        ]
        low_importance = [
            r for r, m in akl_metrics.items() if m.get("importance_score", 0) < 20
        ]

        return {
            "success": True,
            "total_rules": total_rules,
            "total_access_count": total_access_count,
            "average_importance": round(avg_importance, 2),
            "importance_distribution": {
                "high": len(high_importance),
                "medium": len(medium_importance),
                "low": len(low_importance),
            },
            "high_importance_rules": high_importance,
            "medium_importance_rules": medium_importance,
            "low_importance_rules": low_importance,
        }

    def reset_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Reset metrics for a specific rule.

        Args:
            rule_id: Rule ID to reset

        Returns:
            Reset operation result
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_akl_structure(ledger)

        akl_metrics = ledger["memory_cortex"]["akl_metrics"]

        if rule_id not in akl_metrics:
            return {"success": False, "error": f"Rule not found: {rule_id}"}

        # Reset metrics
        akl_metrics[rule_id] = {
            "access_count": 0,
            "last_accessed": "never",
            "importance_score": 0,
            "created_at": "auto_generated",
            "reset_at": "auto_generated",
        }

        ledger["memory_cortex"]["akl_metrics"] = akl_metrics
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "rule_id": rule_id,
            "message": f"Metrics for rule '{rule_id}' reset",
        }


# Singleton instance for convenience
_default_akl_service = None


def get_akl_service(repository: Optional[LedgerRepository] = None) -> AKLService:
    """
    Get AKL service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        AKLService instance
    """
    global _default_akl_service

    if repository is not None:
        return AKLService(repository)

    if _default_akl_service is None:
        _default_akl_service = AKLService()

    return _default_akl_service
