"""---
NC-SUPER-020 — neocortex_evolution
FASE 6 — Evolução governada com sandbox + user approval

WHAT: Sandbox testing via genome replicator fork (BSL-3 default), mutation
      proposal/voting via auto-amendment engine (NC-CORE-FR-136), drift
      status via regression service (NC-CORE-FR-123), and constitutional
      amendment proposals requiring Kernel 0 ratification.
WHY: Phase 6 governed evolution — T0 tests changes in sandboxed child
     instances, proposes amendments to Mutation Board, votes on pending
     mutations, checks system drift against regression baselines, and
     proposes constitutional amendments.
WHERE: Registered as 'neocortex_evolution' — used by T0 evolution workflows,
       sandbox testing pipelines, mutation governance boards, and
       constitutional amendment ratification processes.

Actions: sandbox.test, mutation.propose, mutation.approve,
  mutation.reject, mutation.list, drift.status, constitution.amend
---"""


from datetime import datetime
from pathlib import Path
from typing import Any
from ..errors import mcp_response
TOOL_NAME = "neocortex_evolution"
root = Path(__file__).parents[4]

def _ts(): return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def register_tool(mcp):
    @mcp.tool(name=TOOL_NAME)
    @mcp_response
    def neocortex_evolution(
        action: str,
        child_id: str = "",
        description: str = "",
        mutation_id: str = "",
        bsl_level: int = 3,
    ) -> dict[str, Any]:
        """FASE 6 — Evolução governada com sandbox + user approval.
        Actions:
          sandbox.test     — testar mudança em sandbox (BSL-3 default)
          sandbox.promote  — promover child a staging
          mutation.propose — propor mutação ao Mutation Board
          mutation.approve — T0 aprova mutação
          mutation.reject  — T0 rejeita mutação
          mutation.list    — listar mutações pendentes
          drift.status     — verificar drift do sistema
          constitution.amend — propor emenda (requer Kernel 0)
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

            if action == "sandbox.test":
                spec = importlib.util.spec_from_file_location("genome", str(core / "NC-CORE-FR-130-genome-replicator.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                ok, r = mod.get_genome().fork(f"sandbox-{child_id or 'test'}", bsl_level)
                return {"success": ok, "action": action, "sandbox": r, "bsl": bsl_level, "timestamp": ts}

            elif action == "mutation.propose":
                spec = importlib.util.spec_from_file_location("amend", str(core / "NC-CORE-FR-136-auto-amendment-engine.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                engine = mod.get_amendment_engine()
                r = engine.propose_amendment("GOVERNANCE", description, "proposta via evolution tool")
                return {"success": True, "action": action, "result": r, "timestamp": ts}

            elif action == "mutation.list":
                spec = importlib.util.spec_from_file_location("amend", str(core / "NC-CORE-FR-136-auto-amendment-engine.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                engine = mod.get_amendment_engine()
                proposals = engine.list_amendments()
                return {"success": True, "action": action, "proposals": proposals, "count": len(proposals), "timestamp": ts}

            elif action == "mutation.approve":
                spec = importlib.util.spec_from_file_location("amend", str(core / "NC-CORE-FR-136-auto-amendment-engine.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                engine = mod.get_amendment_engine()
                r = engine.vote_amendment(mutation_id, "favor", "T0")
                return {"success": True, "action": action, "result": r, "timestamp": ts}

            elif action == "mutation.reject":
                spec = importlib.util.spec_from_file_location("amend", str(core / "NC-CORE-FR-136-auto-amendment-engine.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                engine = mod.get_amendment_engine()
                r = engine.vote_amendment(mutation_id, "contra", "T0")
                return {"success": True, "action": action, "result": r, "timestamp": ts}

            elif action == "drift.status":
                spec = importlib.util.spec_from_file_location("reg", str(core / "NC-CORE-FR-123-regression-service.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                svc = mod.get_regression_service()
                r = svc.check()
                return {"success": True, "action": action,
                        "buffer_size": r.get("buffer_size",0),
                        "recent_errors": r.get("recent_errors",[])[:3], "timestamp": ts}

            elif action == "constitution.amend":
                return {"success": True, "action": action,
                        "status": "requer_aprovacao",
                        "note": "Emendas constitucionais requerem Plebiscito (neocortex_governance → plebiscite.propose) + ratificação do Kernel 0",
                        "timestamp": ts}

            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["sandbox.test","mutation.propose","mutation.approve","mutation.reject","mutation.list","drift.status","constitution.amend"], "timestamp": ts}
        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": ts}
