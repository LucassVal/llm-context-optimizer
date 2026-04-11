#!/usr/bin/env python3
"""
Agent Service - Business logic for ephemeral agent orchestration.

This service encapsulates business logic for ephemeral agent operations,
using repository interfaces for storage abstraction.
"""

from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class AgentService:
    """Service for ephemeral agent business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize agent service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                        If None, uses default LedgerStore.
        """
        if repository is None:
            from ..infra.ledger_store import LedgerStore

            self.repository = LedgerStore()
        else:
            self.repository = repository

    def _ensure_agent_structure(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure agent structure exists in memory_cortex."""
        memory_cortex = ledger.get("memory_cortex", {})
        if "active_agents" not in memory_cortex:
            memory_cortex["active_agents"] = []
        if "agent_archive" not in memory_cortex:
            memory_cortex["agent_archive"] = {}
        ledger["memory_cortex"] = memory_cortex
        return ledger

    def spawn_agent(
        self, role: str, backend_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn a new ephemeral agent.

        Args:
            role: Agent role/description
            backend_override: Optional LLM backend override (e.g., "ollama", "deepseek")

        Returns:
            Operation result dictionary
        """
        if not role:
            return {"success": False, "error": "role is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_agent_structure(ledger)

        active_agents = ledger["memory_cortex"]["active_agents"]
        new_agent_id = f"ag-{len(active_agents) + 1:03d}"

        new_agent = {
            "agent_id": new_agent_id,
            "role": role,
            "status": "running",
            "created_at": "auto_generated",
            "lobe_ref": f"ephemeral/{new_agent_id}-{role.replace(' ', '-')}.mdc",
            "parent_task": "Task created via MCP",
        }

        if backend_override:
            new_agent["backend"] = backend_override

        active_agents.append(new_agent)
        ledger["memory_cortex"]["active_agents"] = active_agents
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "agent": new_agent,
            "message": f"Agent {new_agent_id} created with role: {role}"
            + (f" (backend: {backend_override})" if backend_override else ""),
        }

    def list_ephemeral(self) -> Dict[str, Any]:
        """
        List all active ephemeral agents.

        Returns:
            Dictionary with active agents list
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_agent_structure(ledger)

        active_agents = ledger["memory_cortex"]["active_agents"]

        return {
            "success": True,
            "active_agents": active_agents,
            "count": len(active_agents),
        }

    def heartbeat(self, agent_id: str) -> Dict[str, Any]:
        """
        Check agent status (heartbeat).

        Args:
            agent_id: Agent ID to check

        Returns:
            Heartbeat result dictionary
        """
        if not agent_id:
            return {"success": False, "error": "agent_id is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_agent_structure(ledger)

        active_agents = ledger["memory_cortex"]["active_agents"]
        agent = next((a for a in active_agents if a.get("agent_id") == agent_id), None)

        if not agent:
            return {"success": False, "error": f"Agent not found: {agent_id}"}

        return {
            "success": True,
            "agent_id": agent_id,
            "status": agent.get("status", "unknown"),
            "last_heartbeat": "auto_generated",
        }

    def consume(self, agent_id: str) -> Dict[str, Any]:
        """
        Consume agent results and archive agent.

        Args:
            agent_id: Agent ID to consume

        Returns:
            Consumption result dictionary
        """
        if not agent_id:
            return {"success": False, "error": "agent_id is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_agent_structure(ledger)

        memory_cortex = ledger["memory_cortex"]
        active_agents = memory_cortex["active_agents"]
        agent_archive = memory_cortex.get("agent_archive", {})

        agent = next((a for a in active_agents if a.get("agent_id") == agent_id), None)
        if not agent:
            return {"success": False, "error": f"Agent not found: {agent_id}"}

        # Move to archive
        completed = agent_archive.get("completed", [])
        completed.append(agent)
        agent_archive["completed"] = completed
        memory_cortex["agent_archive"] = agent_archive

        # Remove from active
        active_agents = [a for a in active_agents if a.get("agent_id") != agent_id]
        memory_cortex["active_agents"] = active_agents

        ledger["memory_cortex"] = memory_cortex
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "agent_id": agent_id,
            "consumed": True,
            "message": f"Agent {agent_id} archived after consumption",
        }

    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics about agents.

        Returns:
            Dictionary with agent statistics
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_agent_structure(ledger)

        memory_cortex = ledger["memory_cortex"]
        active_agents = memory_cortex["active_agents"]
        agent_archive = memory_cortex.get("agent_archive", {})
        completed = agent_archive.get("completed", [])

        # Calculate role distribution
        role_distribution = {}
        for agent in active_agents:
            role = agent.get("role", "unknown")
            role_distribution[role] = role_distribution.get(role, 0) + 1

        # Calculate status distribution
        status_distribution = {}
        for agent in active_agents:
            status = agent.get("status", "unknown")
            status_distribution[status] = status_distribution.get(status, 0) + 1

        return {
            "success": True,
            "active_count": len(active_agents),
            "completed_count": len(completed),
            "total_agents": len(active_agents) + len(completed),
            "role_distribution": role_distribution,
            "status_distribution": status_distribution,
            "completion_rate": len(completed) / (len(active_agents) + len(completed))
            if (len(active_agents) + len(completed)) > 0
            else 0,
        }


# Singleton instance for convenience
_default_agent_service = None


def get_agent_service(repository: Optional[LedgerRepository] = None) -> AgentService:
    """
    Get agent service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        AgentService instance
    """
    global _default_agent_service

    if repository is not None:
        return AgentService(repository)

    if _default_agent_service is None:
        _default_agent_service = AgentService()

    return _default_agent_service
