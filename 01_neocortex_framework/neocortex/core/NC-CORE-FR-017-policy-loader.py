# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""
NC-SRV-FR-002  PolicyLoader: Reads NC-CFG-FR-001-agent-policy-template.yaml at runtime.
PRE-1 Implementation  integrates policy limits into mentor_step_0 and sub_server.py.

Provides:
  - get_policy(role)  limits, allowed_tools, forbidden_actions, mentor config
  - check_token_limit(role, prompt_len)  (ok, limit, over_by)
  - get_compliance_status()  dict for HUD heartbeat
"""

import logging
import time
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

POLICY_YAML_PATH = (
    Path(__file__).parent.parent.parent
    / "DIR-DOC-FR-001-docs-main"
    / "NC-CFG-FR-001-agent-policy-template.yaml"
)

# Hard-coded safe defaults  used only if YAML is unreadable
DEFAULT_LIMITS: dict[str, Any] = {
    "max_tokens_per_task": 2048,
    "daily_budget_tokens": 50000,
    "daily_budget_usd": 0.50,
    "task_timeout_seconds": 120,
    "max_retries": 3,
    "min_call_interval_seconds": 1,
}

DEFAULT_ALLOWED_TOOLS: dict[str, list[str]] = {
    "courier":     ["neocortex_lobes", "neocortex_search", "neocortex_ledger",
                    "neocortex_task", "neocortex_regression"],
    "engineer":    ["neocortex_lobes", "neocortex_search", "neocortex_ledger",
                    "neocortex_task", "neocortex_regression", "neocortex_cortex",
                    "neocortex_checkpoint"],
    "guardian":    ["neocortex_lobes", "neocortex_search", "neocortex_ledger",
                    "neocortex_regression", "neocortex_security"],
    "backend_dev": [],  # empty = ALL TOOLS
    "unknown":     ["neocortex_lobes", "neocortex_search"],
}

DEFAULT_FORBIDDEN: dict[str, list[str]] = {
    "courier":     ["spawn", "stop", "delete_lobe", "write_ledger", "set_config", "export"],
    "engineer":    ["spawn", "stop", "delete_lobe", "set_config"],
    "guardian":    ["spawn", "stop", "delete_lobe", "write_ledger", "set_config", "export",
                    "update", "create", "delete"],
    "backend_dev": [],
    "unknown":     ["spawn", "stop", "delete_lobe", "write_ledger", "set_config", "export"],
}


class PolicyLoader:
    """
    Loads agent policies from NC-CFG-FR-001-agent-policy-template.yaml.
    Hot-reloads every 120s. Falls back to hard-coded defaults (never crashes).
    """

    def __init__(self, policy_yaml: Path | None = None):
        self._yaml_path = policy_yaml or POLICY_YAML_PATH
        self._raw: dict[str, Any] = {}
        self._loaded: bool = False
        self._last_load: float = 0.0
        self._load_ttl: float = 120.0
        self._token_usage: dict[str, int] = {}  # role  total tokens used today
        self._load()

    def _load(self) -> None:
        if not self._yaml_path.exists():
            logger.warning(f"[PolicyLoader]  Policy YAML not found: {self._yaml_path}. Using defaults.")
            self._loaded = False
            return
        try:
            with open(self._yaml_path, encoding="utf-8") as f:
                self._raw = yaml.safe_load(f) or {}
            self._loaded = True
            self._last_load = time.monotonic()
            logger.info(f"[PolicyLoader]  Policy loaded from {self._yaml_path.name}")
        except Exception as e:
            logger.error(f"[PolicyLoader]  Failed to load policy: {e}. Using defaults.")
            self._loaded = False

    def _maybe_reload(self) -> None:
        if time.monotonic() - self._last_load > self._load_ttl:
            self._load()

    def get_limits(self, role: str = "courier") -> dict[str, Any]:
        """Get resource limits for a role. Falls back to defaults if YAML missing."""
        self._maybe_reload()
        if self._loaded:
            return dict(self._raw.get("agent", {}).get("limits", DEFAULT_LIMITS))
        return dict(DEFAULT_LIMITS)

    def get_allowed_tools(self, role: str = "courier") -> list[str]:
        """Get whitelist of allowed tools for a role."""
        self._maybe_reload()
        if self._loaded:
            tools = self._raw.get("agent", {}).get("allowed_tools", [])
            if tools:
                return list(tools)
        return list(DEFAULT_ALLOWED_TOOLS.get(role, DEFAULT_ALLOWED_TOOLS["unknown"]))

    def get_forbidden_actions(self, role: str = "courier") -> list[str]:
        """Get list of forbidden actions for a role."""
        self._maybe_reload()
        if self._loaded:
            actions = self._raw.get("agent", {}).get("forbidden_actions", [])
            if actions is not None:
                return list(actions)
        return list(DEFAULT_FORBIDDEN.get(role, DEFAULT_FORBIDDEN["unknown"]))

    def get_mentor_prefix(self, role: str = "courier") -> str:
        """Get the mentor_prefix string for the given role."""
        self._maybe_reload()
        if self._loaded:
            pfx = self._raw.get("agent", {}).get("mentor", {}).get("mentor_prefix", "")
            if pfx:
                return str(pfx).strip()
        return ""

    def check_token_limit(self, role: str, prompt_len_chars: int) -> tuple[bool, int, int]:
        """
        Check if prompt length (chars) is within the token budget.
        Approximation: 4 chars  1 token.
        Returns (within_limit, limit_tokens, over_by_tokens).
        """
        limits = self.get_limits(role)
        max_tokens = limits.get("max_tokens_per_task", 2048)
        approx_tokens = prompt_len_chars // 4
        over_by = max(0, approx_tokens - max_tokens)
        return over_by == 0, max_tokens, over_by

    def check_tool_allowed(self, role: str, tool_name: str) -> tuple[bool, str]:
        """Check if tool_name is in the allowed_tools list for role."""
        allowed = self.get_allowed_tools(role)
        if not allowed:  # Empty list = all tools allowed (backend_dev/T0)
            return True, "ALL_TOOLS_ALLOWED"
        if tool_name in allowed:
            return True, "ALLOWED"
        return False, f"TOOL_NOT_IN_WHITELIST: '{tool_name}' not allowed for role '{role}'"

    def check_action_allowed(self, role: str, action: str) -> tuple[bool, str]:
        """Check if action is forbidden for role."""
        forbidden = self.get_forbidden_actions(role)
        if action.lower() in [f.lower() for f in forbidden]:
            return False, f"FORBIDDEN_ACTION: '{action}' not allowed for role '{role}'"
        return True, "ALLOWED"

    def record_token_usage(self, role: str, tokens: int) -> None:
        """Track token usage per role (for daily budget monitoring)."""
        self._token_usage[role] = self._token_usage.get(role, 0) + tokens

    def get_compliance_status(self) -> dict[str, Any]:
        """Returns real-time compliance status for HUD heartbeat."""
        self._maybe_reload()
        limits = self.get_limits()
        usage = dict(self._token_usage)
        age = round(time.monotonic() - self._last_load, 1)
        return {
            "yaml_loaded": self._loaded,
            "yaml_path": str(self._yaml_path),
            "yaml_age_seconds": age,
            "max_tokens_per_task": limits.get("max_tokens_per_task", 2048),
            "daily_budget_usd": limits.get("daily_budget_usd", 0.5),
            "token_usage_by_role": usage,
            "status": " ACTIVE" if self._loaded else " DEFAULTS_ONLY",
        }


#  Singleton
_policy_loader: PolicyLoader | None = None


def get_policy_loader() -> PolicyLoader:
    """Get global PolicyLoader singleton."""
    global _policy_loader
    if _policy_loader is None:
        _policy_loader = PolicyLoader()
    return _policy_loader
