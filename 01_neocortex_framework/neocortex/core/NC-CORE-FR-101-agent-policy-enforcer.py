#!/usr/bin/env python3
"""
NC-CORE-FR-021-agent-policy-enforcer.py — AGENT-001
Carrega e valida policies de agentes locais.

Responsabilidades:
  - Carregar policy YAML por agent_role
  - Validar se tool/action é permitida para o agente
  - Reportar violações ao SecurityService
  - Integrar com CircuitBreaker (token budget)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Diretório de policies
_POLICY_DIR = Path(__file__).parents[3] / "DIR-DS-000-agent-config"
_POLICY_CACHE: Dict[str, Dict] = {}


def _load_policy(role: str) -> Dict[str, Any]:
    """Carrega policy YAML para um role. Cache em memória."""
    if role in _POLICY_CACHE:
        return _POLICY_CACHE[role]

    # Tentar arquivos no padrão NC-CFG-{ROLE}-001-agent-policy.yaml
    candidates = [
        _POLICY_DIR / f"NC-CFG-{role.upper()}-001-agent-policy.yaml",
        _POLICY_DIR / "NC-CFG-DS-001-agent-policy.yaml",  # fallback genérico
    ]

    for path in candidates:
        if path.exists():
            try:
                import yaml
                data = yaml.safe_load(path.read_text("utf-8", errors="replace"))
                policy = data.get("agent", {}) if isinstance(data, dict) else {}
                _POLICY_CACHE[role] = policy
                logger.debug(f"[PolicyEnforcer] Policy carregada: {path.name} para role={role}")
                return policy
            except Exception as e:
                logger.warning(f"[PolicyEnforcer] Erro ao carregar {path.name}: {e}")

    # Fallback: policy mínima restritiva
    logger.warning(f"[PolicyEnforcer] Nenhuma policy encontrada para role={role} — usando mínima")
    minimal = {
        "role": role,
        "tier": "T2",
        "allowed_tools": ["neocortex_health"],
        "forbidden_actions": ["agent.spawn", "lobe.delete", "config.set"],
        "token_budget": {"max_tokens_per_task": 512},
    }
    _POLICY_CACHE[role] = minimal
    return minimal


def reload_policy(role: str) -> None:
    """Força reload da policy (invalida cache)."""
    _POLICY_CACHE.pop(role, None)
    _load_policy(role)


class AgentPolicyEnforcer:
    """
    Valida permissões de agentes locais com base nas policies YAML.

    Usage:
        enforcer = AgentPolicyEnforcer("courier")
        enforcer.check_tool("neocortex_memory")     # OK
        enforcer.check_tool("neocortex_governance")  # raises PolicyViolationError
        enforcer.check_action("lobe.delete")         # raises PolicyViolationError
    """

    def __init__(self, role: str):
        self.role   = role.lower()
        self.policy = _load_policy(self.role)

    # ── Tool check ────────────────────────────────────────────────────────────

    def check_tool(self, tool_name: str, raise_on_violation: bool = True) -> bool:
        """Verifica se uma tool MCP é permitida para este agente."""
        allowed = self.policy.get("allowed_tools", [])
        # Wildcard "*" = tudo permitido (apenas T0)
        if "*" in allowed or tool_name in allowed:
            return True
        if raise_on_violation:
            raise PolicyViolationError(
                f"[{self.role}] Tool '{tool_name}' não está na whitelist. "
                f"Permitidas: {allowed}"
            )
        return False

    # ── Action check ──────────────────────────────────────────────────────────

    def check_action(self, action: str, raise_on_violation: bool = True) -> bool:
        """Verifica se uma action está na lista proibida."""
        forbidden = self.policy.get("forbidden_actions", [])
        if action in forbidden:
            if raise_on_violation:
                raise PolicyViolationError(
                    f"[{self.role}] Action '{action}' é PROIBIDA pela policy."
                )
            return False
        return True

    # ── Lobe check ────────────────────────────────────────────────────────────

    def check_lobe_write(self, lobe_name: str, raise_on_violation: bool = True) -> bool:
        """Verifica se o agente pode escrever em um lobe."""
        import fnmatch
        write_allowed = self.policy.get("allowed_lobes", {}).get("write", [])
        for pattern in write_allowed:
            if fnmatch.fnmatch(lobe_name, pattern):
                return True
        if raise_on_violation:
            raise PolicyViolationError(
                f"[{self.role}] Escrita no lobe '{lobe_name}' não autorizada. "
                f"Write-allowed: {write_allowed}"
            )
        return False

    def check_lobe_read(self, lobe_name: str) -> bool:
        """Verifica se o agente pode ler um lobe (permissivo por padrão)."""
        import fnmatch
        read_allowed = self.policy.get("allowed_lobes", {}).get("read", ["NC-LBE-*"])
        return any(fnmatch.fnmatch(lobe_name, p) for p in read_allowed)

    # ── Token budget ──────────────────────────────────────────────────────────

    def get_token_budget(self) -> Dict[str, int]:
        """Retorna budget de tokens para este agente."""
        return self.policy.get("token_budget", {
            "max_tokens_per_task": 1024,
            "max_tokens_session": 8192,
        })

    # ── Circuit Breaker config ─────────────────────────────────────────────────

    def get_cb_config(self) -> Dict[str, Any]:
        """Retorna config para o CircuitBreaker deste agente."""
        return self.policy.get("circuit_breaker", {
            "max_calls": 20,
            "window_sec": 60,
            "max_identical": 5,
            "cooldown_sec": 120,
        })

    # ── Full validate ─────────────────────────────────────────────────────────

    def validate_call(self, tool: str, action: str, lobe: str = "") -> Dict[str, Any]:
        """Validação completa de uma chamada. Retorna dict com resultado."""
        violations = []
        try:
            self.check_tool(tool)
        except PolicyViolationError as e:
            violations.append(str(e))

        try:
            self.check_action(action)
        except PolicyViolationError as e:
            violations.append(str(e))

        if lobe and "write" in action:
            try:
                self.check_lobe_write(lobe)
            except PolicyViolationError as e:
                violations.append(str(e))

        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "role": self.role,
            "tier": self.policy.get("tier", "T2"),
        }

    # ── Info ──────────────────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        return {
            "role":            self.role,
            "tier":            self.policy.get("tier", "T2"),
            "model":           self.policy.get("backend", {}).get("model", "?"),
            "allowed_tools":   self.policy.get("allowed_tools", []),
            "forbidden_count": len(self.policy.get("forbidden_actions", [])),
            "token_budget":    self.get_token_budget(),
            "cb_config":       self.get_cb_config(),
        }


# ── Exceção ───────────────────────────────────────────────────────────────────

class PolicyViolationError(PermissionError):
    """Raised quando um agente tenta uma ação não autorizada pela policy."""
    pass


# ── Registry de enforcers ─────────────────────────────────────────────────────

_enforcer_cache: Dict[str, AgentPolicyEnforcer] = {}


def get_enforcer(role: str) -> AgentPolicyEnforcer:
    if role not in _enforcer_cache:
        _enforcer_cache[role] = AgentPolicyEnforcer(role)
    return _enforcer_cache[role]


def list_policies() -> List[Dict[str, Any]]:
    """Lista todas as policies disponíveis em DIR-DS-000-agent-config."""
    policies = []
    if _POLICY_DIR.exists():
        for f in sorted(_POLICY_DIR.glob("NC-CFG-*-agent-policy.yaml")):
            enforcer = get_enforcer(f.stem.split("-")[2].lower())
            policies.append(enforcer.summary())
    return policies
