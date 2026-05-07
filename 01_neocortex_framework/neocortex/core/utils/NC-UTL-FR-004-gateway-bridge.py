# @UBL @UBL @UTL-FR | LEXICO: #SYSTEM
"""---
@Tool NC-UTL-FR-004-gateway-bridge mcp NC-UTL-FR-004-gateway-bridge.py — Gateway Bridge (
---
"""


import importlib.util
from pathlib import Path
from typing import Any

_GATEWAY = None


def _get_gateway():
    global _GATEWAY
    if _GATEWAY is not None:
        return _GATEWAY
    spec = importlib.util.spec_from_file_location(
        "gateway",
        str(Path(__file__).parents[1] / "NC-CORE-FR-129-shared-kernel-gateway.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _GATEWAY = mod.get_gateway()
    return _GATEWAY


def gateway_check(action: str, root: Path, agent_id: str = "T0",
                  agent_role: str = "T0", target_path: str = "",
                  check_str: str = "", full_context: dict[str, Any] | None = None) -> tuple[bool, dict[str, Any]]:
    """
    Súmula Vinculante: toda ação passa por esta porteira.
    Retorna (allowed: bool, report: dict).
    """
    try:
        gw = _get_gateway()
        return gw.validate_action(
            action=action,
            root=root,
            agent_id=agent_id,
            agent_role=agent_role,
            target_path=target_path,
            check_str=check_str,
            full_context=full_context or {},
        )
    except Exception as e:
        # Fail-secure: se gateway indisponível, BLOQUEIA
        return False, {
            "allowed": False,
            "error": f"Gateway indisponível: {e}",
            "violations": [f"GATEWAY DOWN: {e}"],
            "checks": {},
        }
