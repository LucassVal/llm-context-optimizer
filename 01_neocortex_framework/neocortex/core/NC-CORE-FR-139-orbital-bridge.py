# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Tool NC-CORE-FR-139-orbital-bridge mcp NC-CORE-FR-139-orbital-bridge.py — Ponte Orbital p
---
"""


import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Any

ACTIONS = {
    # CPC Digital — (filename, mod_key, method, param_mapping)
    "cpc.process": ("NC-CORE-FR-132-civil-procedure-code.py", "cpc", "process_action",
                    {"action": None, "target_path": "target_path",
                     "agent_id": "agent_id", "agent_role": "agent_role",
                     "urgency": None}),
    "cpc.appeal": ("NC-CORE-FR-132-civil-procedure-code.py", "cpc", "appeal",
                   {"case_id": "case_id", "grounds": "description"}),
    # CPP Digital
    "cpp.check": ("NC-CORE-FR-135-criminal-procedure-code.py", "cpp", "check_prisoner",
                  {"agent_id": "agent_id"}),
    "cpp.prisoners": ("NC-CORE-FR-135-criminal-procedure-code.py", "cpp", "list_prisoners", {}),
    # Legislative
    "plebiscite.propose": ("NC-CORE-FR-134-legislative-process.py", "leg", "propose_plebiscite",
                           {"question": "title", "options": None, "proposer": "agent_id"}),
    "congress.list": ("NC-CORE-FR-134-legislative-process.py", "leg", "list_bills", {}),
    "emergency.mp": ("NC-CORE-FR-134-legislative-process.py", "leg", "emergency_decree",
                     {"title": "title", "action": "description", "kernel_authorization": None}),
    # Regulatory
    "regulatory.health": ("NC-CORE-FR-133-regulatory-agencies.py", "reg", "full_audit", {}),
    # Genome
    "genome.fork": ("NC-CORE-FR-130-genome-replicator.py", "genome", "fork", {}),
    "genome.children": ("NC-CORE-FR-130-genome-replicator.py", "genome", "list_children", {}),
    # Vigilant
    "vigilant.status": ("NC-CORE-FR-137-vigilant-cycle.py", "vig", "get_status", {}),
    # Hierarchy Protocol
    "hierarchy.comm_log": ("NC-CORE-FR-140-hierarchy-protocol.py", "hierarchy", "get_communication_log", {}),
    # Secretariats
    "saude.health": ("NC-CORE-FR-141-secretariats.py", "secretariats", "saude.system_health", {}),
    "trabalho.stats": ("NC-CORE-FR-141-secretariats.py", "secretariats", "trabalho.get_agent_stats", {}),
    "fazenda.budget": ("NC-CORE-FR-141-secretariats.py", "secretariats", "fazenda.check_budget", {}),
    # Organs
    "tcu.audit": ("NC-CORE-FR-138-judicial-organs.py", "organs", "audit_wal", {}),
}

# Default param values for None mappings
DEFAULTS = {
    "options": ["sim", "nao"],
    "kernel_authorization": True,
    "grounds": "recurso via MCP",
    "action": "mcp_call",
    "target_path": "",
    "agent_id": "T0",
    "agent_role": "T0",
    "urgency": "normal",
    "proposer": "T0",
    "case_id": "",
}

_cache: dict[str, Any] = {}


def _load_module(root: Path, filename: str):
    if filename in _cache:
        return _cache[filename]
    core = root / "01_neocortex_framework" / "neocortex" / "core"
    spec = importlib.util.spec_from_file_location(filename.replace(".py", ""), str(core / filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _cache[filename] = mod
    return mod


def orbital_dispatch(action: str, root: Path, **kwargs) -> dict[str, Any] | None:
    """
    Orbital Bridge — dispatch para módulos jurídicos.
    R22 DRY (Súmula Vinculante): toda ação passa pelo gateway ANTES de despachar.
    Tool chama esta função para ações que não reconhece.
    Retorna None se a ação não for tratada (tool continua seu dispatch normal).
    """
    if action not in ACTIONS:
        return None

    # ── SÚMULA VINCULANTE (DRY): Gateway check BEFORE dispatch ──
    try:
        from neocortex.core.utils.gateway_bridge import gateway_check
        _ok, _report = gateway_check(action, root)
        if not _ok:
            return _report
    except Exception:
        pass  # gateway indisponível — não bloqueia (fail-open controlado)

    filename, mod_key, method_path, param_map = ACTIONS[action]
    try:
        mod = _load_module(root, filename)

        obj = mod
        if mod_key == "cpc": obj = mod.get_cpc()
        elif mod_key == "cpp": obj = mod.get_cpp()
        elif mod_key == "leg": obj = mod.get_legislative()
        elif mod_key == "reg": obj = mod.get_regulatory()
        elif mod_key == "genome": obj = mod.get_genome()
        elif mod_key == "vig": obj = mod.get_vigilant_cycle()
        elif mod_key == "organs": obj = mod.get_judicial_organs()
        elif mod_key == "hierarchy": obj = mod.get_hierarchy()
        elif mod_key == "secretariats": obj = mod.get_secretariats()

        # Resolver dot notation e construir kwargs
        for part in method_path.split("."):
            obj = getattr(obj, part)

        # Mapear parâmetros do MCP para o método
        call_kwargs = {}
        for method_param, mcp_param in param_map.items():
            if mcp_param is None:
                call_kwargs[method_param] = DEFAULTS.get(method_param, "")
            elif mcp_param in kwargs:
                call_kwargs[method_param] = kwargs[mcp_param]
            else:
                call_kwargs[method_param] = DEFAULTS.get(method_param, "")

        ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        result = obj(**call_kwargs)
        return {"success": True, "action": action, "result": result, "timestamp": ts}

    except Exception as e:
        return {"success": False, "action": action, "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
