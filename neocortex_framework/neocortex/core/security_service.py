#!/usr/bin/env python3
"""
Security Service - Business logic for security operations.

This service encapsulates business logic for security operations,
using repository interfaces for storage abstraction.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..repositories import LedgerRepository

# Check if advanced security utils are available
try:
    from ..core.security_utils import can_access

    SECURITY_UTILS_AVAILABLE = True
except ImportError:
    SECURITY_UTILS_AVAILABLE = False


class SecurityService:
    """Service for security-related business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize security service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLedgerRepository.
        """
        if repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.repository = FileSystemLedgerRepository()
        else:
            self.repository = repository

    def validate_access(
        self,
        current_user_id: str = "",
        target_user_id: str = "",
        access_type: str = "read",
        resource: str = "",
    ) -> Dict[str, Any]:
        """
        Validate access to resources.

        Args:
            current_user_id: ID of current user (if empty, uses ledger's user_context)
            target_user_id: ID of target user (if empty, uses resource as target)
            access_type: 'read' or 'write' (default: read)
            resource: Resource to access (alternative to target_user_id)

        Returns:
            Validation result dictionary
        """
        ledger = self.repository.read_ledger()

        # Initialize security log if not exists
        memory_cortex = ledger.get("memory_cortex", {})
        if "security_log" not in memory_cortex:
            memory_cortex["security_log"] = []
            ledger["memory_cortex"] = memory_cortex

        security_log = memory_cortex.get("security_log", [])

        # Determine current user ID
        if not current_user_id:
            user_context = ledger.get("user_context", {})
            current_user_id = user_context.get("current_user_id", "")
            if not current_user_id:
                return {
                    "success": False,
                    "error": "current_user_id not specified and not found in ledger",
                }

        # Determine target user ID
        if not target_user_id:
            target_user_id = (
                resource  # Use resource as target user ID for backward compatibility
            )

        if not target_user_id:
            return {
                "success": False,
                "error": "target_user_id or resource is required",
            }

        # Use hierarchical access control if available, otherwise simulate
        reason = "simulated_fallback"
        if SECURITY_UTILS_AVAILABLE:
            allowed, reason = can_access(current_user_id, target_user_id, access_type)
            access_granted = allowed
            validation_method = "hierarchical_access_control"
            validation_details = {"reason": reason}
        else:
            # Fallback simulation
            access_granted = True
            validation_method = "cortex_rule_check_fallback"
            validation_details = {"note": "security_utils_not_available"}
            reason = "security_utils_not_available"

        # Prepare validation record
        access_validation = {
            "resource": resource,
            "current_user_id": current_user_id,
            "target_user_id": target_user_id,
            "access_type": access_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "access_granted": access_granted,
            "validation_method": validation_method,
            "validation_details": validation_details,
            "message": f"Acesso {access_type} de '{current_user_id}' para '{target_user_id}' {'permitido' if access_granted else 'negado'}",
        }

        # Log the validation
        security_log.append(
            {
                "type": "access_validation",
                "current_user_id": current_user_id,
                "target_user_id": target_user_id,
                "access_type": access_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "outcome": "granted" if access_granted else "denied",
                "reason": reason if SECURITY_UTILS_AVAILABLE else "simulated",
            }
        )
        memory_cortex["security_log"] = security_log
        ledger["memory_cortex"] = memory_cortex
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "validation": access_validation,
            "message": f"Access validation completed: {access_validation['message']}",
        }

    def audit_changes(self) -> Dict[str, Any]:
        """
        Get audit history.

        Returns:
            Dictionary with recent audit entries
        """
        ledger = self.repository.read_ledger()
        memory_cortex = ledger.get("memory_cortex", {})
        security_log = memory_cortex.get("security_log", [])

        # Return recent audits (last 10 entries)
        recent_audits = security_log[-10:] if security_log else []

        return {
            "success": True,
            "audit_log": recent_audits,
            "total_entries": len(security_log),
            "message": f"{len(recent_audits)} recent entries in audit log",
        }

    def encrypt_sensitive(self, resource: str) -> Dict[str, Any]:
        """
        Mark sensitive resource for encryption.

        Args:
            resource: Resource to encrypt

        Returns:
            Dictionary with encryption record
        """
        if not resource:
            return {"success": False, "error": "resource is required"}

        ledger = self.repository.read_ledger()
        memory_cortex = ledger.get("memory_cortex", {})
        security_log = memory_cortex.get("security_log", [])

        # Simulation of encryption
        encryption_record = {
            "resource": resource,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "encryption_applied": True,
            "method": "simulated_aes256",
            "key_id": f"key_{resource.replace('/', '_')}",
        }

        # Register in log
        security_log.append(
            {
                "type": "encryption_applied",
                "resource": resource,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "method": "simulated",
            }
        )
        memory_cortex["security_log"] = security_log
        ledger["memory_cortex"] = memory_cortex
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "encryption": encryption_record,
            "message": f"Resource '{resource}' marked for encryption",
        }

    def get_security_log(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get security log with optional limit.

        Args:
            limit: Maximum number of entries to return

        Returns:
            Dictionary with security log entries
        """
        ledger = self.repository.read_ledger()
        memory_cortex = ledger.get("memory_cortex", {})
        security_log = memory_cortex.get("security_log", [])

        # Apply limit
        if limit > 0:
            entries = security_log[-limit:]
        else:
            entries = security_log

        # Categorize entries by type
        by_type = {}
        for entry in entries:
            entry_type = entry.get("type", "unknown")
            if entry_type not in by_type:
                by_type[entry_type] = 0
            by_type[entry_type] += 1

        return {
            "success": True,
            "entries": entries,
            "total_entries": len(security_log),
            "showing": len(entries),
            "by_type": by_type,
        }


# Singleton instance for convenience
_default_security_service = None


def get_security_service(
    repository: Optional[LedgerRepository] = None,
) -> SecurityService:
    """
    Get security service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        SecurityService instance
    """
    global _default_security_service

    if repository is not None:
        return SecurityService(repository)

    if _default_security_service is None:
        _default_security_service = SecurityService()

    return _default_security_service
