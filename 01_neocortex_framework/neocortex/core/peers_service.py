#!/usr/bin/env python3
"""
Peers Service - Business logic for peer coordination.

This service encapsulates business logic for peer coordination operations,
using repository interfaces for storage abstraction.
"""

from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class PeersService:
    """Service for peer coordination business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize peers service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                        If None, uses default LedgerStore.
        """
        if repository is None:
            from ..infra.ledger_store import LedgerStore

            self.repository = LedgerStore()
        else:
            self.repository = repository

    def _ensure_peers_structure(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure peers structure exists in memory_cortex."""
        memory_cortex = ledger.get("memory_cortex", {})
        if "peers" not in memory_cortex:
            memory_cortex["peers"] = []
            ledger["memory_cortex"] = memory_cortex
        return ledger

    def discover(self) -> Dict[str, Any]:
        """
        Discover available peers.

        Returns:
            Dictionary with discovered peers
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_peers_structure(ledger)

        peers = ledger["memory_cortex"]["peers"]

        return {
            "success": True,
            "peers": peers,
            "count": len(peers),
            "message": f"{len(peers)} peers available",
        }

    def sync_state(self, peer_id: str, state_data: str = "") -> Dict[str, Any]:
        """
        Synchronize state with a peer.

        Args:
            peer_id: Peer ID to sync with
            state_data: State data to synchronize

        Returns:
            Synchronization result dictionary
        """
        if not peer_id:
            return {"success": False, "error": "peer_id is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_peers_structure(ledger)

        memory_cortex = ledger["memory_cortex"]
        peers = memory_cortex["peers"]

        # Synchronization simulation
        sync_record = {
            "peer_id": peer_id,
            "timestamp": "auto_generated",
            "state_synced": True,
            "data_preview": state_data[:100] if state_data else "empty",
        }

        # Add peer if it doesn't exist
        existing_peer = next((p for p in peers if p.get("id") == peer_id), None)
        if not existing_peer:
            peers.append({"id": peer_id, "last_sync": "now", "status": "active"})
            memory_cortex["peers"] = peers
            ledger["memory_cortex"] = memory_cortex
            self.repository.write_ledger(ledger)

        return {
            "success": True,
            "sync_record": sync_record,
            "message": f"State synchronized with peer '{peer_id}'",
        }

    def resolve_conflict(self, peer_id: str) -> Dict[str, Any]:
        """
        Resolve state conflicts with a peer.

        Args:
            peer_id: Peer ID to resolve conflicts with

        Returns:
            Conflict resolution dictionary
        """
        if not peer_id:
            return {"success": False, "error": "peer_id is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_peers_structure(ledger)

        peers = ledger["memory_cortex"]["peers"]

        # Conflict resolution simulation
        conflict_resolution = {
            "conflict_id": f"conflict_{peer_id}_{len(peers)}",
            "peer_id": peer_id,
            "resolution": "merge_auto",
            "timestamp": "auto_generated",
            "message": "Conflict resolved via automatic merge",
        }

        return {
            "success": True,
            "resolution": conflict_resolution,
            "message": f"Conflict with peer '{peer_id}' resolved",
        }

    def add_peer(self, peer_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add a new peer.

        Args:
            peer_id: Peer ID
            metadata: Optional peer metadata

        Returns:
            Operation result dictionary
        """
        if not peer_id:
            return {"success": False, "error": "peer_id is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_peers_structure(ledger)

        memory_cortex = ledger["memory_cortex"]
        peers = memory_cortex["peers"]

        # Check if peer already exists
        existing_peer = next((p for p in peers if p.get("id") == peer_id), None)
        if existing_peer:
            return {
                "success": True,
                "peer_id": peer_id,
                "existing": True,
                "message": f"Peer '{peer_id}' already exists",
            }

        # Create new peer entry
        new_peer = {
            "id": peer_id,
            "status": "active",
            "last_sync": "never",
            "metadata": metadata or {},
            "created_at": "auto_generated",
        }

        peers.append(new_peer)
        memory_cortex["peers"] = peers
        ledger["memory_cortex"] = memory_cortex
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "peer": new_peer,
            "message": f"Peer '{peer_id}' added successfully",
        }

    def remove_peer(self, peer_id: str) -> Dict[str, Any]:
        """
        Remove a peer.

        Args:
            peer_id: Peer ID to remove

        Returns:
            Operation result dictionary
        """
        if not peer_id:
            return {"success": False, "error": "peer_id is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_peers_structure(ledger)

        memory_cortex = ledger["memory_cortex"]
        peers = memory_cortex["peers"]

        # Find and remove peer
        original_count = len(peers)
        peers = [p for p in peers if p.get("id") != peer_id]
        removed_count = original_count - len(peers)

        if removed_count == 0:
            return {"success": False, "error": f"Peer not found: {peer_id}"}

        memory_cortex["peers"] = peers
        ledger["memory_cortex"] = memory_cortex
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "peer_id": peer_id,
            "removed": True,
            "message": f"Peer '{peer_id}' removed successfully",
        }

    def get_peer_stats(self) -> Dict[str, Any]:
        """
        Get peer statistics.

        Returns:
            Peer statistics dictionary
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_peers_structure(ledger)

        peers = ledger["memory_cortex"]["peers"]

        if not peers:
            return {
                "success": True,
                "total_peers": 0,
                "message": "No peers configured",
            }

        # Calculate statistics
        active_peers = [p for p in peers if p.get("status") == "active"]
        inactive_peers = [p for p in peers if p.get("status") != "active"]

        # Analyze sync status
        never_synced = [p for p in peers if p.get("last_sync") == "never"]
        recently_synced = [p for p in peers if p.get("last_sync") == "now"]

        return {
            "success": True,
            "total_peers": len(peers),
            "active_peers": len(active_peers),
            "inactive_peers": len(inactive_peers),
            "never_synced": len(never_synced),
            "recently_synced": len(recently_synced),
            "sync_coverage": f"{(len(recently_synced) / len(peers)) * 100:.1f}%"
            if peers
            else "0%",
        }


# Singleton instance for convenience
_default_peers_service = None


def get_peers_service(repository: Optional[LedgerRepository] = None) -> PeersService:
    """
    Get peers service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        PeersService instance
    """
    global _default_peers_service

    if repository is not None:
        return PeersService(repository)

    if _default_peers_service is None:
        _default_peers_service = PeersService()

    return _default_peers_service
