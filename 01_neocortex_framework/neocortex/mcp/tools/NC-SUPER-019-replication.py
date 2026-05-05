"""---
@Module NC-SUPER-019-replication mcp NC-SUPER-019-replication.py — neocortex_replicatio
---
"""


from datetime import datetime
from pathlib import Path
from typing import Any

TOOL_NAME = "neocortex_replication"
root = Path(__file__).parents[4]

def _ts(): return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def register_tool(mcp):
    @mcp.tool(name=TOOL_NAME)
    def neocortex_replication(
        action: str,
        child_id: str = "",
        bsl_level: int = 1,
        task: str = "",
    ) -> dict[str, Any]:
        """FASE 6 — Replicação governada para agentes.
        Actions:
          genome.fork      — criar child (herda políticas, BSL sandbox)
          genome.children  — listar réplicas
          instance.switch  — alternar para child
          instance.execute — executar tarefa no child
          instance.status  — status do child atual
        """
        ts = _ts()
        # ── GATEWAY VALIDATION ──────────────────────────────
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok:
                return _report
        except Exception:
            pass

        try:
            import importlib.util
            core = root / "01_neocortex_framework" / "neocortex" / "core"

            if action == "genome.fork":
                spec = importlib.util.spec_from_file_location("genome", str(core / "NC-CORE-FR-130-genome-replicator.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                ok, r = mod.get_genome().fork(child_id or "", bsl_level)
                return {"success": ok, "action": action, "result": r, "timestamp": ts}

            elif action == "genome.children":
                spec = importlib.util.spec_from_file_location("genome", str(core / "NC-CORE-FR-130-genome-replicator.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                children = mod.get_genome().list_children()
                return {"success": True, "action": action, "children": children, "count": len(children), "timestamp": ts}

            elif action == "instance.switch":
                spec = importlib.util.spec_from_file_location("inst", str(core / "NC-CORE-FR-145-lightweight-instances.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                mgr = mod.get_instance_manager()
                r = mgr.switch(child_id)
                return {"success": True, "action": action, "result": r, "timestamp": ts}

            elif action == "instance.execute":
                spec = importlib.util.spec_from_file_location("inst", str(core / "NC-CORE-FR-145-lightweight-instances.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                mgr = mod.get_instance_manager()
                r = mgr.execute(task)
                return {"success": True, "action": action, "result": r, "timestamp": ts}

            elif action == "instance.status":
                spec = importlib.util.spec_from_file_location("inst", str(core / "NC-CORE-FR-145-lightweight-instances.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                mgr = mod.get_instance_manager()
                r = mgr.get_current()
                return {"success": True, "action": action, "current": r, "timestamp": ts}

            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["genome.fork","genome.children","instance.switch","instance.execute","instance.status"], "timestamp": ts}
        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": ts}
