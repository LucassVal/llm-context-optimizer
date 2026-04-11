#!/usr/bin/env python3
"""
Checkpoint Service - Business logic for checkpoint and timeline operations.

This service encapsulates business logic for checkpoint management,
using repository interfaces for storage abstraction.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class CheckpointService:
    """Service for checkpoint and timeline business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize checkpoint service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                        If None, uses default LedgerStore.
        """
        if repository is None:
            from ..infra.ledger_store import LedgerStore

            self.repository = LedgerStore()
        else:
            self.repository = repository

    def get_current_checkpoint(self) -> Dict[str, Any]:
        """
        Get current checkpoint from memory cortex.

        Returns:
            Dictionary with current checkpoint information
        """
        ledger = self.repository.read_ledger()

        memory_cortex = ledger.get("memory_cortex", {})
        synapses = memory_cortex.get("synapses", {})
        current_context = synapses.get("current_context", {})

        return {
            "success": True,
            "current_checkpoint": current_context.get("checkpoint_id", "None"),
            "current_lobe": current_context.get("lobe_id", "None"),
            "has_context": bool(current_context),
            "synapses_metadata": {
                "total_synapses": len(synapses),
                "has_memory_cortex": "memory_cortex" in ledger,
            },
        }

    def set_current_checkpoint(
        self, checkpoint_id: str, description: str = "", lobe_id: str = "00-cortex"
    ) -> Dict[str, Any]:
        """
        Set a new current checkpoint.

        Args:
            checkpoint_id: ID of the checkpoint
            description: Optional description
            lobe_id: Lobe ID (default: "00-cortex")

        Returns:
            Dictionary with operation result
        """
        if not checkpoint_id:
            return {"success": False, "error": "checkpoint_id is required"}

        ledger = self.repository.read_ledger()

        # Ensure memory_cortex structure exists
        if "memory_cortex" not in ledger:
            ledger["memory_cortex"] = {}

        memory_cortex = ledger["memory_cortex"]

        if "synapses" not in memory_cortex:
            memory_cortex["synapses"] = {}

        synapses = memory_cortex["synapses"]

        # Set current context
        synapses["current_context"] = {
            "lobe_id": lobe_id,
            "checkpoint_id": checkpoint_id,
            "set_at": datetime.now().isoformat(),
        }

        # Update global checkpoint index
        if "global_checkpoint_index" not in memory_cortex:
            memory_cortex["global_checkpoint_index"] = {}

        global_index = memory_cortex["global_checkpoint_index"]

        if "checkpoints" not in global_index:
            global_index["checkpoints"] = []

        checkpoints = global_index["checkpoints"]
        if checkpoint_id not in checkpoints:
            checkpoints.append(checkpoint_id)
            global_index["checkpoints"] = checkpoints
            memory_cortex["global_checkpoint_index"] = global_index

        memory_cortex["synapses"] = synapses
        ledger["memory_cortex"] = memory_cortex

        # Update timeline
        if "session_timeline" not in ledger:
            ledger["session_timeline"] = []

        timeline = ledger["session_timeline"]
        timeline.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "checkpoint_set",
                "checkpoint_id": checkpoint_id,
                "lobe_id": lobe_id,
                "description": description or f"Checkpoint set via CheckpointService",
            }
        )
        ledger["session_timeline"] = timeline

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "lobe_id": lobe_id,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "total_checkpoints": len(checkpoints),
                "timeline_length": len(timeline),
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def complete_task(self, task_name: str) -> Dict[str, Any]:
        """
        Mark a task as completed in action queue.

        Args:
            task_name: Name of the task to complete

        Returns:
            Dictionary with operation result
        """
        if not task_name:
            return {"success": False, "error": "task_name is required"}

        ledger = self.repository.read_ledger()

        # Ensure action_queue structure exists
        if "action_queue" not in ledger:
            ledger["action_queue"] = {"pending": [], "in_progress": [], "completed": []}

        action_queue = ledger["action_queue"]
        pending = action_queue.get("pending", [])
        in_progress = action_queue.get("in_progress", [])
        completed = action_queue.get("completed", [])

        # Find and move task
        moved = False
        if task_name in pending:
            pending.remove(task_name)
            moved = True
        elif task_name in in_progress:
            in_progress.remove(task_name)
            moved = True

        if not moved:
            return {
                "success": False,
                "error": f"Task '{task_name}' not found in pending or in_progress",
                "pending_count": len(pending),
                "in_progress_count": len(in_progress),
            }

        # Add to completed
        completed.append(task_name)

        # Update action queue
        action_queue.update(
            {"pending": pending, "in_progress": in_progress, "completed": completed}
        )
        ledger["action_queue"] = action_queue

        # Add to timeline
        if "session_timeline" not in ledger:
            ledger["session_timeline"] = []

        timeline = ledger["session_timeline"]
        timeline.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "task_completed",
                "task_name": task_name,
                "description": f"Task '{task_name}' completed via CheckpointService",
            }
        )
        ledger["session_timeline"] = timeline

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "task": task_name,
                "status": "completed",
                "pending_tasks": len(pending),
                "in_progress_tasks": len(in_progress),
                "completed_tasks": len(completed),
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def list_checkpoint_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        List checkpoint history from timeline.

        Args:
            limit: Maximum number of events to return

        Returns:
            Dictionary with timeline history
        """
        ledger = self.repository.read_ledger()

        timeline = ledger.get("session_timeline", [])

        # Filter checkpoint-related events
        checkpoint_events = [
            event
            for event in timeline
            if event.get("event") in ["checkpoint_set", "task_completed"]
        ]

        # Get recent events
        recent_events = checkpoint_events[-limit:] if limit > 0 else checkpoint_events

        # Calculate statistics
        total_events = len(timeline)
        checkpoint_events_count = len(checkpoint_events)

        # Group by event type
        event_types = {}
        for event in timeline:
            event_type = event.get("event", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "success": True,
            "history": recent_events,
            "total_timeline_events": total_events,
            "checkpoint_related_events": checkpoint_events_count,
            "event_type_distribution": event_types,
            "limit_applied": limit,
        }

    def get_global_checkpoint_index(self) -> Dict[str, Any]:
        """
        Get global checkpoint index.

        Returns:
            Dictionary with checkpoint index
        """
        ledger = self.repository.read_ledger()

        memory_cortex = ledger.get("memory_cortex", {})
        global_index = memory_cortex.get("global_checkpoint_index", {})
        checkpoints = global_index.get("checkpoints", [])

        # Get checkpoint metadata if available
        checkpoint_details = []
        for checkpoint_id in checkpoints:
            # Look for timeline events for this checkpoint
            timeline = ledger.get("session_timeline", [])
            checkpoint_events = [
                event
                for event in timeline
                if event.get("checkpoint_id") == checkpoint_id
            ]

            checkpoint_details.append(
                {
                    "id": checkpoint_id,
                    "event_count": len(checkpoint_events),
                    "first_seen": checkpoint_events[0].get("timestamp")
                    if checkpoint_events
                    else None,
                    "last_seen": checkpoint_events[-1].get("timestamp")
                    if checkpoint_events
                    else None,
                }
            )

        return {
            "success": True,
            "checkpoints": checkpoints,
            "checkpoint_details": checkpoint_details,
            "total_checkpoints": len(checkpoints),
            "has_global_index": "global_checkpoint_index" in memory_cortex,
        }

    def add_timeline_event(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add custom event to timeline.

        Args:
            event_type: Type of event
            data: Event data

        Returns:
            Dictionary with operation result
        """
        if not event_type:
            return {"success": False, "error": "event_type is required"}

        ledger = self.repository.read_ledger()

        if "session_timeline" not in ledger:
            ledger["session_timeline"] = []

        timeline = ledger["session_timeline"]

        event = {"timestamp": datetime.now().isoformat(), "event": event_type, **data}

        timeline.append(event)
        ledger["session_timeline"] = timeline

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "event": event,
                "timeline_length": len(timeline),
                "message": f"Event '{event_type}' added to timeline",
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def force_checkpoint(self) -> Dict[str, Any]:
        """
        Force creation of an automatic checkpoint.

        Creates a checkpoint with auto-generated ID and adds timeline event.

        Returns:
            Dictionary with operation result
        """
        from datetime import datetime
        import uuid

        # Generate checkpoint ID
        checkpoint_id = f"CP-AUTO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

        result = self.set_current_checkpoint(
            checkpoint_id=checkpoint_id,
            description="Auto-checkpoint created by PulseScheduler",
            lobe_id="NC-LBE-FR-002-claude-assistant",
        )

        if result.get("success"):
            # Also add timeline event
            self.add_timeline_event(
                event_type="auto_checkpoint",
                data={
                    "checkpoint_id": checkpoint_id,
                    "source": "pulse_scheduler",
                    "description": "Automatic checkpoint",
                },
            )

        return result


# Singleton instance for convenience
_default_checkpoint_service = None


def get_checkpoint_service(
    repository: Optional[LedgerRepository] = None,
) -> CheckpointService:
    """
    Get checkpoint service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        CheckpointService instance
    """
    global _default_checkpoint_service

    if repository is not None:
        return CheckpointService(repository)

    if _default_checkpoint_service is None:
        _default_checkpoint_service = CheckpointService()

    return _default_checkpoint_service
