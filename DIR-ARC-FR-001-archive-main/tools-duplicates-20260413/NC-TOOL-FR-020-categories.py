"""
NC-TOOL-FR-020-categories.py
Tool Hub  Agrupa as 22 ferramentas em 6 categorias lgicas.

Em vez de 22 entries no manifest do MCP, expe 6 super-tools:
  neocortex_memory      cortex, lobes, manifest, export, init, search
  neocortex_session     checkpoint, regression, savepoint, ledger, pulse
  neocortex_agents      agent, task, subserver, peers, benchmark
  neocortex_config      config, security, report
  neocortex_knowledge   brain (DeepSeek), project_manifest
  neocortex_system      factory, scan, health

Cada super-tool aceita: action="<subtool>.<action>" ou apenas "help".

Design decision:
  A IA NO fica "preguiosa" com grupos  na verdade fica MAIS ASSERTIVA porque:
  1. Menos ferramentas visveis  menos ambiguidade na escolha
  2. O "help" de cada categoria j lista as sub-aes disponveis
  3. O manifesto continua granular internamente (JSONL por arquivo)
  4. A IA usa neocortex_memory(action="lobes.list_active") em vez de
     neocortex_lobes(action="list_active")  mesma assertividade, menos overhead MCP
"""
from __future__ import annotations

import json
from pathlib import Path

_TOOLS_DIR = Path(__file__).parent

#  Mapa de categorias  (subtool_module, allowed_actions) 
CATEGORY_MAP = {
    "memory": {
        "desc": "Memria e conhecimento  cortex, lobes, export, busca",
        "tools": {
            "cortex":    ("NC-TOOL-FR-001-cortex",    ["get_full", "get_section", "get_aliases", "get_workflows"]),
            "lobes":     ("NC-TOOL-FR-009-lobes",     ["list_active", "get_content", "activate", "deactivate", "search", "list_all"]),
            "manifest":  ("NC-TOOL-FR-018-manifest",  ["generate", "update", "query", "get", "list", "delete"]),
            "export":    ("NC-TOOL-FR-006-export",    ["to_markdown", "to_json", "to_graph", "export_lobes"]),
            "init":      ("NC-TOOL-FR-007-init",      ["scan_project", "generate_cortex", "generate_lobe"]),
            "search":    ("NC-TOOL-FR-014-search",    ["search"]),
        },
    },
    "session": {
        "desc": "Estado e integridade da sesso  checkpoints, rollback, ledger",
        "tools": {
            "checkpoint": ("NC-TOOL-FR-004-checkpoint",  ["get_current", "set_current", "complete_task", "list_history", "list_index"]),
            "regression": ("NC-TOOL-FR-012-regression",  ["check", "add_entry", "list_all", "clear", "stats"]),
            "savepoint":  ("NC-TOOL-FR-031-savepoint",   ["list_active", "rollback", "discard", "get_status"]),
            "ledger":     ("NC-TOOL-FR-008-ledger",      ["get_metrics", "get_atomic_locks", "get_dependency_graph", "prune_context"]),
            "pulse":      ("NC-TOOL-FR-011-pulse",       ["status", "force", "start", "stop"]),
        },
    },
    "agents": {
        "desc": "Orquestrao de agentes  ephemeral, tasks, sub-servidores",
        "tools": {
            "agent":     ("NC-TOOL-FR-002-agent",     ["spawn", "heartbeat", "consume", "list_ephemeral"]),
            "task":      ("NC-TOOL-FR-017-task",      ["execute", "list_queued", "get_result", "cancel"]),
            "subserver": ("NC-TOOL-FR-016-subserver", ["spawn", "stop", "list_active", "send_task", "health"]),
            "peers":     ("NC-TOOL-FR-010-peers",     ["discover", "sync_state", "resolve_conflict"]),
            "benchmark": ("NC-TOOL-FR-003-benchmark", ["run_drift", "run_titanomachy", "get_last_report"]),
        },
    },
    "config": {
        "desc": "Configurao, segurana e relatrios do sistema",
        "tools": {
            "config":   ("NC-TOOL-FR-005-config",    ["get_config", "set_model", "list_models", "set_constraint", "list_constraints", "set_agent_backend"]),
            "security": ("NC-TOOL-FR-015-security",  ["validate_access", "audit_changes", "encrypt_sensitive"]),
            "report":   ("NC-TOOL-FR-013-report",    ["generate_daily_summary", "generate_cost_report", "generate_agent_report", "get_metrics_stats"]),
        },
    },
    "knowledge": {
        "desc": "Motor de raciocnio e manifesto de projeto  DeepSeek T-0",
        "tools": {
            "brain":            ("NC-TOOL-FR-000-brain",          ["think", "plan", "orchestrate"]),
            "project_manifest": ("NC-TOOL-FR-019-project-manifest", ["generate", "get_boot_context", "get_nc_index", "get_structure", "get_ssot_files"]),
        },
    },
}


def _load_tool_module(nc_id: str):
    """Import tardio de mdulo NC-TOOL via importlib.util (R09 compliance)."""
    import importlib.util
    path = _TOOLS_DIR / f"{nc_id}.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(nc_id.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _help(category: str) -> str:
    cat = CATEGORY_MAP.get(category)
    if not cat:
        cats = ", ".join(CATEGORY_MAP.keys())
        return json.dumps({"error": f"Categoria '{category}' desconhecida", "valid": cats})
    out = {"category": f"neocortex_{category}", "desc": cat["desc"], "sub_tools": {}}
    for subtool, (nc_id, actions) in cat["tools"].items():
        out["sub_tools"][subtool] = {"nc_id": nc_id, "actions": actions}
    out["usage"] = f"neocortex_{category}(action='<subtool>.<action>', **kwargs)"
    out["example"] = f"neocortex_{category}(action='{list(cat['tools'].keys())[0]}.{cat['tools'][list(cat['tools'].keys())[0]][1][0]}')"
    return json.dumps(out, ensure_ascii=False, indent=2)


def _dispatch(category: str, action: str, kwargs: dict) -> str:
    """Despacha action='subtool.subaction' para o mdulo correto."""
    if not action or action == "help":
        return _help(category)

    parts = action.split(".", 1)
    if len(parts) != 2:
        return json.dumps({
            "error": "Formato invlido. Use 'subtool.action', ex: 'lobes.list_active'",
            "received": action,
        })

    subtool_name, subaction = parts
    cat = CATEGORY_MAP.get(category, {})
    tools = cat.get("tools", {})

    if subtool_name not in tools:
        return json.dumps({
            "error": f"Subtool '{subtool_name}' no existe em '{category}'",
            "valid_subtools": list(tools.keys()),
        })

    nc_id, allowed = tools[subtool_name]

    # Tenta usar o mdulo NC-TOOL diretamente via FastMCP/server (j registrado)
    # Se no disponvel, chama via importlib
    try:
        mod = _load_tool_module(nc_id)
        if mod is None:
            return json.dumps({"error": f"Mdulo {nc_id}.py no encontrado"})

        # Encontra a funo de tool no mdulo
        # Conveno: a tool se chama neocortex_<subtool_name>
        tool_func_name = f"neocortex_{subtool_name}"
        # Registra em um MockMCP mnimo para recuperar a funo
        func_holder = {}
        class _MockServer:
            def tool(self, name=None):
                def deco(f):
                    func_holder[name or f.__name__] = f
                    return f
                return deco
        mod.register_tool(_MockServer())
        fn = func_holder.get(tool_func_name) or func_holder.get(list(func_holder.keys())[0] if func_holder else None)
        if fn is None:
            return json.dumps({"error": f"Funo {tool_func_name} no encontrada em {nc_id}"})
        return fn(action=subaction, **kwargs)
    except Exception as e:
        import traceback
        return json.dumps({"error": str(e), "trace": traceback.format_exc()[-400:]})


def register_tool(server):
    """Registra as 6 super-tools no servidor MCP."""

    @server.tool()
    def neocortex_memory(action: str = "help", **kwargs) -> str:
        """memoria: cortex, lobes, manifest, export, init, search | action='subtool.acao'"""
        return _dispatch("memory", action, kwargs)

    @server.tool()
    def neocortex_session(action: str = "help", **kwargs) -> str:
        """sessao: checkpoint, regression, savepoint, ledger, pulse | action='subtool.acao'"""
        return _dispatch("session", action, kwargs)

    @server.tool()
    def neocortex_agents(action: str = "help", **kwargs) -> str:
        """agentes: agent, task, subserver, peers, benchmark | action='subtool.acao'"""
        return _dispatch("agents", action, kwargs)

    @server.tool()
    def neocortex_config(action: str = "help", **kwargs) -> str:
        """config: config, security, report | action='subtool.acao'"""
        return _dispatch("config", action, kwargs)

    @server.tool()
    def neocortex_knowledge(action: str = "help", **kwargs) -> str:
        """conhecimento: brain (DeepSeek T-0), project_manifest | action='subtool.acao'"""
        return _dispatch("knowledge", action, kwargs)
