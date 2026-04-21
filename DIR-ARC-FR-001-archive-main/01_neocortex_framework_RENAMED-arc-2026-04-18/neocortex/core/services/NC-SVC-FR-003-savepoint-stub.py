"""---
domain: "core"
layer: "core"
type: "file"
tags: ["svc", "003", "savepoint", "stub"]
hash: "auto-generated"
---"""
"""
NC-SVC-FR-003-savepoint-stub.py
FR-003  SavePoint Service: WAL/SavePoint stub for NeoCortex.

Provides stub SavePoint and SavePointService classes for savepoint management.
All methods return dicts; real persistence requires WAL (SAVE-005 phase 2).

Restriction: server.py, sub_server.py, pulse_scheduler.py are @LOCKS.
This module is a stub; real implementation will be integrated after WAL.
"""

import time
import uuid
from typing import Any, Dict, List


class SavePoint:
    """SavePoint representation (stub)."""

    def __init__(self, state_snapshot: Dict[str, Any], ttl_seconds: int = 3600):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.state_snapshot = state_snapshot
        self.ttl_seconds = ttl_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert SavePoint to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "state_snapshot": self.state_snapshot,
            "ttl_seconds": self.ttl_seconds,
        }


class SavePointService:
    """SavePoint service stub."""

    _savepoints: Dict[str, SavePoint] = {}

    @classmethod
    def create(
        cls, state_snapshot: Dict[str, Any], ttl_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Create a new SavePoint.

        Args:
            state_snapshot: Arbitrary state dictionary
            ttl_seconds: Timetolive in seconds (default 1 hour)

        Returns:
            Dictionary with created SavePoint data.
        """
        sp = SavePoint(state_snapshot, ttl_seconds)
        cls._savepoints[sp.id] = sp
        return sp.to_dict()

    @classmethod
    def list_active(cls) -> List[Dict[str, Any]]:
        """
        List all active (nonexpired) SavePoints.

        Returns:
            List of SavePoint dictionaries.
        """
        now = time.time()
        active = []
        for sp in cls._savepoints.values():
            if now - sp.timestamp < sp.ttl_seconds:
                active.append(sp.to_dict())
        return active

    @classmethod
    def rollback(cls, savepoint_id: str) -> Dict[str, Any]:
        """
        Rollback to a specific SavePoint (stub).

        Args:
            savepoint_id: ID of the SavePoint to rollback to

        Returns:
            Dictionary with rollback status and snapshot.
        """
        sp = cls._savepoints.get(savepoint_id)
        if sp is None:
            return {"status": "error", "message": "SavePoint not found"}
        # In a real implementation this would restore state
        return {
            "status": "success",
            "message": "STUB  rollback not actually performed",
            "savepoint": sp.to_dict(),
        }

    @classmethod
    def discard(cls, savepoint_id: str) -> Dict[str, Any]:
        """
        Discard a SavePoint.

        Args:
            savepoint_id: ID of the SavePoint to discard

        Returns:
            Dictionary with discard status.
        """
        if savepoint_id not in cls._savepoints:
            return {"status": "error", "message": "SavePoint not found"}
        del cls._savepoints[savepoint_id]
        return {"status": "success", "message": "SavePoint discarded"}


# Convenience functions


def create_savepoint(
    state_snapshot: Dict[str, Any], ttl_seconds: int = 3600
) -> Dict[str, Any]:
    """Create a SavePoint and return its data."""
    return SavePointService.create(state_snapshot, ttl_seconds)


def list_active_savepoints() -> List[Dict[str, Any]]:
    """Return list of active SavePoints."""
    return SavePointService.list_active()


def rollback_to_savepoint(savepoint_id: str) -> Dict[str, Any]:
    """Rollback to a specific SavePoint (stub)."""
    return SavePointService.rollback(savepoint_id)


def discard_savepoint(savepoint_id: str) -> Dict[str, Any]:
    """Discard a SavePoint."""
    return SavePointService.discard(savepoint_id)


# STUB  persistncia real requer WAL (SAVE-005 fase 2)
