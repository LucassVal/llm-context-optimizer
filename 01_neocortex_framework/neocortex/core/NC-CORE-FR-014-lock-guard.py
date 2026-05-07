# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""
NC-SRV-FR-001  LockGuard: Path-Based Atomic Lock Enforcer
SEC-401 Implementation  reads NC-SEC-FR-001-atomic-locks.yaml at runtime.

Replaces the previous simulated SecurityService fallback (access_granted=True).
DENY BY DEFAULT. Only explicitly listed exceptions are allowed.

Usage:
    from neocortex.core.lock_guard import LockGuard, get_lock_guard
    guard = get_lock_guard()
    allowed, reason = guard.check_write(path="neocortex/mcp/server.py", agent_role="courier")
    #  (False, "BLOCKED: mcp_server lock group")
"""

import fnmatch
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Path to the atomic locks YAML (relative to 01_neocortex_framework/)
LOCKS_YAML_PATH = (
    Path(__file__).parent.parent.parent
    / "DIR-DOC-FR-001-docs-main"
    / "NC-SEC-FR-001-atomic-locks.yaml"
)


class LockGuard:
    """
    Path-based atomic lock enforcer.
    Reads NC-SEC-FR-001-atomic-locks.yaml and blocks writes to protected paths.

    SEC-401: This replaces the broken SecurityService fallback (access_granted=True).
    DENY BY DEFAULT  if locks YAML is missing, ALL writes are blocked.
    """

    def __init__(self, locks_yaml: Path | None = None):
        self._locks_yaml = locks_yaml or LOCKS_YAML_PATH
        self._config: dict[str, Any] = {}
        self._locked_patterns: list[dict[str, Any]] = []  # [{group, action, patterns}]
        self._exceptions: list[dict[str, Any]] = []
        self._last_load_time: float = 0.0
        self._load_ttl: float = 60.0  # Reload YAML every 60s
        self._violation_log: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load and parse the locks YAML. DENY ALL if YAML missing or corrupt."""
        if not self._locks_yaml.exists():
            logger.critical(
                f"[LockGuard]  NC-SEC-FR-001-atomic-locks.yaml NOT FOUND at {self._locks_yaml}. "
                "ALL WRITES DENIED (fail-safe)."
            )
            self._locked_patterns = [{"group": "FAILSAFE", "action": "block_write", "patterns": ["**/*"]}]
            self._exceptions = []
            return

        try:
            with open(self._locks_yaml, encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

            locks_section = self._config.get("atomic_locks", {})
            self._locked_patterns = []
            for group_name, group_data in locks_section.items():
                if not isinstance(group_data, dict):
                    continue
                action = group_data.get("action", "block_write")
                paths = group_data.get("paths", [])
                if paths:
                    self._locked_patterns.append({
                        "group": group_name,
                        "action": action,
                        "patterns": [str(p) for p in paths],
                    })

            self._exceptions = self._config.get("exceptions", [])
            self._last_load_time = time.monotonic()
            logger.info(
                f"[LockGuard]  Loaded {len(self._locked_patterns)} lock groups "
                f"+ {len(self._exceptions)} exceptions from {self._locks_yaml.name}"
            )
        except Exception as e:
            logger.critical(f"[LockGuard]  Failed to parse locks YAML: {e}. DENY ALL.")
            self._locked_patterns = [{"group": "PARSE_ERROR", "action": "block_write", "patterns": ["**/*"]}]
            self._exceptions = []

    def _maybe_reload(self) -> None:
        """Hot-reload the YAML if TTL expired (allows runtime updates without restart)."""
        if time.monotonic() - self._last_load_time > self._load_ttl:
            self._load()

    def _matches_any(self, path_str: str, patterns: list[str]) -> bool:
        """Check if path_str matches any glob pattern in the list."""
        # Normalize to forward slashes for consistent matching
        normalized = path_str.replace("\\", "/").lstrip("/")
        for pattern in patterns:
            pat = pattern.replace("\\", "/").lstrip("/")
            # Try direct fnmatch
            if fnmatch.fnmatch(normalized, pat):
                return True
            # Try with just the filename
            if fnmatch.fnmatch(Path(normalized).name, pat):
                return True
            # Recursive glob: **/* matches everything
            if pat == "**/*" or pat == "**":
                return True
            # Handle **/ prefix (match any subdirectory)
            if "**" in pat:
                # Convert ** to something fnmatch can handle
                simple_pat = pat.replace("**/", "*/")
                if fnmatch.fnmatch(normalized, simple_pat):
                    return True
                # Try matching the suffix
                suffix = pat.lstrip("*").lstrip("/")
                if suffix and normalized.endswith(suffix):
                    return True
        return False

    def _is_excepted(self, path_str: str, agent_role: str) -> tuple[bool, str]:
        """Check if agent_role has an explicit exception for this path."""
        for exc in self._exceptions:
            if exc.get("agent_role") != agent_role:
                continue
            allowed_write = exc.get("allowed_write", [])
            if self._matches_any(path_str, allowed_write):
                reason = exc.get("reason", "explicit exception")
                return True, reason
        return False, ""

    def check_write(self, path: str, agent_role: str = "unknown") -> tuple[bool, str]:
        """
        Check if agent_role can write to path.
        Returns (allowed: bool, reason: str).
        DENY BY DEFAULT for blocked paths.
        """
        self._maybe_reload()

        # Check exceptions first (allow overrides)
        excepted, exc_reason = self._is_excepted(path, agent_role)

        for lock_group in self._locked_patterns:
            group = lock_group["group"]
            action = lock_group["action"]
            patterns = lock_group["patterns"]

            if not self._matches_any(path, patterns):
                continue

            # Path matches a lock group
            if action in ("block_write", "FAILSAFE", "PARSE_ERROR"):
                if excepted:
                    logger.info(f"[LockGuard]   {path} matched lock group '{group}' but EXCEPTED for role '{agent_role}': {exc_reason}")
                    return True, f"EXCEPTED: {exc_reason}"

                # DENY
                reason = f"BLOCKED: lock group '{group}' (action={action}). Agent '{agent_role}' has no write permission."
                self._violation_log.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "path": path,
                    "agent_role": agent_role,
                    "lock_group": group,
                    "reason": reason,
                })
                logger.warning(f"[LockGuard]  WRITE DENIED  {path} | {reason}")
                return False, reason

            elif action == "block_cross_write":
                # Cross-lobe isolation: deny if agent_role's lobe != path's lobe
                if "lobes/" in path:
                    path_lobe = path.split("lobes/")[1].split("/", maxsplit=1)[0] if "lobes/" in path else ""
                    agent_lobe = agent_role.replace("_", "-")
                    if path_lobe and path_lobe != agent_lobe and agent_role != "unknown":
                        reason = f"CROSS-LOBE WRITE DENIED: '{agent_role}' cannot write to lobe '{path_lobe}'"
                        self._violation_log.append({
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "path": path, "agent_role": agent_role,
                            "lock_group": group, "reason": reason,
                        })
                        logger.warning(f"[LockGuard]  {reason}")
                        return False, reason

        return True, "ALLOWED: no lock group matched"

    def check_tool_call(self, tool_name: str, action: str, agent_role: str) -> tuple[bool, str]:
        """
        Check if agent_role can execute a specific tool action.
        Used by policy enforcement (NC-CFG-FR-001 forbidden_actions).
        """
        # Map tool+action to forbidden_actions list names
        forbidden_map: dict[str, list[str]] = {
            "courier":     ["spawn", "stop", "delete_lobe", "write_ledger", "set_config", "export"],
            "engineer":    ["spawn", "stop", "delete_lobe", "set_config"],
            "guardian":    ["spawn", "stop", "delete_lobe", "write_ledger", "set_config", "export",
                           "update", "create", "delete"],
            "backend_dev": [],  # T0  no restrictions
            "unknown":     ["spawn", "stop", "delete_lobe", "write_ledger", "set_config", "export"],
        }
        forbidden = forbidden_map.get(agent_role, forbidden_map["unknown"])
        if action.lower() in forbidden:
            reason = f"FORBIDDEN ACTION: '{action}' not allowed for role '{agent_role}'"
            logger.warning(f"[LockGuard]  {reason}")
            return False, reason
        return True, "ALLOWED"

    def get_compliance_status(self) -> dict[str, Any]:
        """
        Returns real-time compliance status for the HUD.
        Checks: YAML loaded, lock groups active, recent violations, reload age.
        """
        self._maybe_reload()
        yaml_ok = self._locks_yaml.exists()
        failsafe = any(lg["group"] in ("FAILSAFE", "PARSE_ERROR") for lg in self._locked_patterns)
        recent_violations = list(self._violation_log[-20:])
        age_seconds = round(time.monotonic() - self._last_load_time, 1)

        return {
            "yaml_loaded": yaml_ok,
            "failsafe_active": failsafe,
            "lock_groups": len(self._locked_patterns),
            "exceptions": len(self._exceptions),
            "violations_total": len(self._violation_log),
            "recent_violations": recent_violations[-5:],
            "yaml_age_seconds": age_seconds,
            "status": " FAILSAFE" if failsafe else (" ACTIVE" if yaml_ok else " NO_YAML"),
        }

    def get_violations(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent violations for audit display."""
        return self._violation_log[-limit:]


#  Singleton
_lock_guard: LockGuard | None = None


def get_lock_guard() -> LockGuard:
    """Get the global LockGuard singleton. Created on first call."""
    global _lock_guard
    if _lock_guard is None:
        _lock_guard = LockGuard()
    return _lock_guard
