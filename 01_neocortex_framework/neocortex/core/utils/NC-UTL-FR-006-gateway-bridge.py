"""---
@Tool  mcp bridge: Gateway → Tools MCP (Shared Kernel) ÚNICO
---
"""


import importlib.util
from pathlib import Path
from typing import Any, Dict, Tuple

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
                  agent_role: str = "T0", target_path: str = "") -> Tuple[bool, Dict[str, Any]]:
    """Súmula Vinculante: toda ação passa por esta porteira."""
    try:
        gw = _get_gateway()
        return gw.validate_action(
            action=action,
            target_path=target_path,
            agent_id=agent_id,
            agent_role=agent_role,
        )
    except Exception as e:
        return False, {
            "allowed": False,
            "error": "Gateway indisponível",
            "violations": [f"GATEWAY DOWN: {e}"],
            "checks": {},
        }
