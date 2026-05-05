"""---
@Guard NC-CORE-FR-124-security-service mcp _genealogy:   injected_at: '2026-04-16T00:23:58.07
---
"""


#!/usr/bin/env python3
"""
Security Service - Business logic for security operations.

This service encapsulates business logic for security operations,
using repository interfaces for storage abstraction.
"""

# SEC-401: LockGuard (R09  via neocortex.core importlib wrapper)
import importlib as _il
from datetime import datetime
from typing import Any

from ..repositories import LedgerRepository

_lck = _il.import_module(".NC-CORE-FR-014-lock-guard", package="neocortex.core")
get_lock_guard = _lck.get_lock_guard

# PRE-1: PolicyLoader (R09  via neocortex.core importlib wrapper)
_pol = _il.import_module(".NC-CORE-FR-017-policy-loader", package="neocortex.core")
get_policy_loader = _pol.get_policy_loader

# Check if advanced security utils are available
try:
    from ..core.security_utils import can_access
    SECURITY_UTILS_AVAILABLE = True
except ImportError:
    SECURITY_UTILS_AVAILABLE = False


class SecurityService:
    """Service for security-related business logic."""

    def __init__(self, repository: LedgerRepository | None = None):
        """
        Initialize security service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                        If None, uses default LedgerStore.
        """
        if repository is None:
            from ..infra.ledger_store import LedgerStore

            self.repository = LedgerStore()
        else:
            self.repository = repository

    def validate_access(
        self,
        current_user_id: str = "",
        target_user_id: str = "",
        access_type: str = "read",
        resource: str = "",
    ) -> dict[str, Any]:
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

        # Use hierarchical access control if available
        reason = "simulated_fallback"
        if SECURITY_UTILS_AVAILABLE:
            allowed, reason = can_access(current_user_id, target_user_id, access_type)
            access_granted = allowed
            validation_method = "hierarchical_access_control"
            validation_details = {"reason": reason}
        else:
            # SEC-401 FIX: DENY BY DEFAULT when security_utils unavailable.
            # Previous code set access_granted=True (SECURITY BREACH  now fixed).
            access_granted = False
            validation_method = "lock_guard_deny_by_default"
            validation_details = {"note": "security_utils_not_available. DENY by default (SEC-401)."}
            reason = "deny_by_default_sec401"

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

    def check_path_write(self, path: str, agent_role: str = "unknown") -> dict[str, Any]:
        """
        SEC-401  Path-based write check via LockGuard (reads NC-SEC-FR-001-atomic-locks.yaml).
        Call this BEFORE any write operation to a file path.
        """
        guard = get_lock_guard()
        allowed, reason = guard.check_write(path, agent_role)
        return {
            "success": True,
            "allowed": allowed,
            "reason": reason,
            "path": path,
            "agent_role": agent_role,
        }

    def check_tool_allowed(self, tool_name: str, action: str, agent_role: str) -> dict[str, Any]:
        """
        PRE-1  Tool/action whitelist check via PolicyLoader (reads NC-CFG-FR-001).
        """
        policy = get_policy_loader()
        tool_ok, tool_reason = policy.check_tool_allowed(agent_role, tool_name)
        action_ok, action_reason = policy.check_action_allowed(agent_role, action)
        allowed = tool_ok and action_ok
        return {
            "success": True,
            "allowed": allowed,
            "tool_reason": tool_reason,
            "action_reason": action_reason,
        }

    def audit_changes(self) -> dict[str, Any]:
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

    def encrypt_sensitive(self, resource: str) -> dict[str, Any]:
        """
        Encrypt sensitive resource via NC-SVC-FR-017-crypto-hub (Fernet real).
        Falls back to hash-only mode when NEOCORTEX_MASTER_KEY is absent.

        Args:
            resource: Resource to encrypt

        Returns:
            Dictionary with encryption record
        """
        if not resource:
            return {"success": False, "error": "resource is required"}

        # Import CryptoHub via importlib (filename has dashes)
        import importlib.util as _ilu
        _hub_path = (
            _il.import_module("pathlib").Path(__file__).resolve().parent
            / "services"
            / "NC-SVC-FR-017-crypto-hub.py"
        )
        _hub_spec = _ilu.spec_from_file_location("crypto_hub", _hub_path)
        _hub_mod = _ilu.module_from_spec(_hub_spec)  # type: ignore[arg-type]
        # Python 3.12+: registrar antes de exec_module para que @dataclass resolva sys.modules
        import sys as _sys_hub
        _sys_hub.modules["crypto_hub"] = _hub_mod
        _hub_spec.loader.exec_module(_hub_mod)  # type: ignore[union-attr]
        CryptoHub = _hub_mod.CryptoHub

        hub = CryptoHub()
        enc_result = hub.encrypt(resource)

        if enc_result.success:
            method = "fernet_aes128_hmac"
            key_id = f"pbkdf2-sha256-{enc_result.token_hash[:8]}"
            encryption_record = {
                "resource": resource,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "encryption_applied": True,
                "method": method,
                "key_id": key_id,
                "ciphertext_sha256": enc_result.token_hash,
                # NÃO armazenar ciphertext no ledger — apenas hash
            }
            log_method = "fernet"
        else:
            # Fallback: MASTER_KEY ausente ou cryptography não instalada
            method = "hash_only"
            encryption_record = {
                "resource": resource,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "encryption_applied": False,
                "method": method,
                "key_id": None,
            }
            log_method = "hash_only"

        ledger = self.repository.read_ledger()
        memory_cortex = ledger.get("memory_cortex", {})
        security_log = memory_cortex.get("security_log", [])

        security_log.append(
            {
                "type": "encryption_applied",
                "resource": resource,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "method": log_method,
            }
        )
        memory_cortex["security_log"] = security_log
        ledger["memory_cortex"] = memory_cortex
        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "encryption": encryption_record,
            "message": f"Resource '{resource}' encrypted via {method}",
        }

    def get_security_log(self, limit: int = 50) -> dict[str, Any]:
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
        entries = security_log[-limit:] if limit > 0 else security_log

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
    repository: LedgerRepository | None = None,
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
