# @UBL @UBL @SUPER-002 | LEXICO: #MCP
#!/usr/bin/env python3
"""---
NC-SUPER-002 — neocortex_orchestration
PODER EXECUTIVO

WHAT: Task orchestration (execute/list/cancel/status), agent lifecycle
      (spawn/heartbeat/consume/list), Ollama worker spawning, cascade
      consolidation, and agent policy enforcement — with graceful degradation
      when backend services are unavailable.
WHY: Fuse 6 fragmented tools (orchestration, agent, task x2, subserver,
     run) into one executive entry point for T1/T2 task delegation through
     unified task pipeline. PicoClaw dispatch removed 2026-05-05.
WHERE: Registered as 'neocortex_orchestration' — used by agent code and CLI
       workflows to enqueue tasks, monitor agent health, and route work.

Actions: task.execute, task.list, task.cancel, task.status,
  agent.spawn, agent.heartbeat, agent.consume, agent.list,
  workers.spawn, workers.status, cascade.run, cascade.status,
  policy.check, policy.list, agent.list_ephemeral, task.get_result
---
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from ..errors import mcp_response
logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_orchestration"

# ── CONSTANTS ──────────────────────────────────────────────────────────────
OLLAMA_BASE = "http://localhost:11434"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def _get_orchestration_service():
    try:
        from neocortex.core.orchestration_service import get_orchestration_service
        return get_orchestration_service()
    except Exception:
        return None


def _get_task_queue():
    try:
        from neocortex.core import get_task_queue_service
        return get_task_queue_service()
    except Exception:
        return None


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    @mcp_response
    def neocortex_orchestration(
        action: str,
        task_name: str = "",
        task_type: str = "generic",
        task_payload: str = "{}",
        agent_id: str = "",
        agent_type: str = "T2",
        priority: int = 5,
        n_workers: int = 1,
        timeout: int = 60,
        dispatch_id: str = "",
    ) -> dict[str, Any]:
        """PODER EXECUTIVO — Execução de tasks, agentes e workers.
        Funde: orchestration, agent, task (ambos), subserver, picoclaw, run.
        Actions: task.execute, task.list, task.cancel, task.status,
                 agent.spawn, agent.heartbeat, agent.consume, agent.list,
                 dispatch.create, dispatch.status,
                 workers.spawn, workers.status
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

        # ── TASKS ─────────────────────────────────────────────────────────────
        if action == "task.execute":
            svc = _get_orchestration_service()
            if svc is None:
                return {"success": False, "error": "OrchestrationService indisponível", "timestamp": ts}
            try:
                payload = json.loads(task_payload) if task_payload else {}
                result = svc.execute_task(name=task_name, task_type=task_type,
                                           payload=payload, priority=priority)
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "task.list":
            q = _get_task_queue()
            if q is None:
                return {"success": False, "error": "TaskQueue indisponível", "timestamp": ts}
            try:
                tasks = q.list_tasks()
                return {"success": True, "action": action, "tasks": tasks,
                        "count": len(tasks), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "task.cancel":
            if not task_name:
                return {"success": False, "error": "task_name obrigatório", "timestamp": ts}
            q = _get_task_queue()
            if q:
                try:
                    q.cancel_task(task_name)
                    return {"success": True, "action": action, "cancelled": task_name, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "TaskQueue indisponível", "timestamp": ts}

        elif action == "task.status":
            q = _get_task_queue()
            if q is None:
                return {"success": True, "action": action, "status": "queue_unavailable",
                        "timestamp": ts}
            try:
                status = q.get_status()
                return {"success": True, "action": action, "queue_status": status, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── AGENTS ────────────────────────────────────────────────────────────
        elif action == "agent.spawn":
            svc = _get_orchestration_service()
            if svc is None:
                return {"success": False, "error": "OrchestrationService indisponível", "timestamp": ts}
            try:
                result = svc.spawn_agent(agent_type=agent_type, task_name=task_name)
                return {"success": True, "action": action, "agent": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "agent.heartbeat":
            svc = _get_orchestration_service()
            if svc:
                try:
                    result = svc.agent_heartbeat(agent_id=agent_id)
                    return {"success": True, "action": action, "heartbeat": result, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "OrchestrationService indisponível", "timestamp": ts}

        elif action == "agent.list":
            svc = _get_orchestration_service()
            if svc:
                try:
                    agents = svc.list_agents()
                    return {"success": True, "action": action, "agents": agents,
                            "count": len(agents), "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": True, "action": action, "agents": [], "count": 0,
                    "note": "OrchestrationService indisponível", "timestamp": ts}

        elif action == "agent.consume":
            svc = _get_orchestration_service()
            if svc:
                try:
                    result = svc.consume_task(agent_id=agent_id, task_type=task_type)
                    return {"success": True, "action": action, "consumed": result, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "OrchestrationService indisponível", "timestamp": ts}

        # ── WORKERS ───────────────────────────────────────────────────────────
        elif action == "workers.spawn":
            spawned = []
            for i in range(min(n_workers, 10)):
                try:
                    import requests
                    r = requests.post(
                        f"{OLLAMA_BASE}/api/generate",
                        json={"model": "qwen2.5-coder:1.5b", "prompt": "ping", "stream": False},
                        timeout=30,
                    )
                    spawned.append({"worker": i + 1, "ok": r.status_code == 200})
                except Exception as e:
                    spawned.append({"worker": i + 1, "ok": False, "error": str(e)})
            return {"success": True, "action": action, "n_workers": n_workers,
                    "results": spawned,
                    "online": sum(1 for w in spawned if w.get("ok")), "timestamp": ts}

        elif action == "workers.status":
            try:
                import requests
                r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
                models = r.json().get("models", []) if r.ok else []
                return {"success": True, "action": action, "ollama_online": r.ok,
                        "models": [m.get("name") for m in models],
                        "worker_model": "qwen2.5-coder:1.5b", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}


        elif action == "agent.list_ephemeral":
            try:
                from neocortex.core import get_agent_service
                svc = get_agent_service()
                result = svc.list_ephemeral_agents() if hasattr(svc, "list_ephemeral_agents") else {"agents": []}
                return {"success": True, "action": action, "agents": result.get("agents", []), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "task.get_result":
            if not task_payload:
                return {"success": False, "error": "task_payload (task_id JSON) obrigatorio", "timestamp": ts}
            try:
                import json as _j
                task_id = _j.loads(task_payload).get("task_id", "")
                from neocortex.services.NC_SVC_FR_015_TaskBroker import TaskBroker
                broker = TaskBroker()
                result = broker.get_result(task_id) if hasattr(broker, "get_result") else {"result": None}
                return {"success": True, "action": action, "task_id": task_id, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── POLICY (AGENT-001) ────────────────────────────────────────────────
        elif action == "policy.check":
            if not agent_id:
                return {"success": False, "error": "agent_id (role) obrigatório", "timestamp": ts}
            try:
                from neocortex.core.agent_policy_enforcer import get_enforcer
                enforcer = get_enforcer(agent_id)
                result = enforcer.validate_call(
                    tool=task_type or "",
                     action=task_name or "",
                )
                return {"success": True, "action": action, "role": agent_id,
                        "allowed": result["allowed"], "violations": result["violations"],
                        "summary": enforcer.summary(), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "policy.list":
            try:
                from neocortex.core.agent_policy_enforcer import list_policies
                policies = list_policies()
                return {"success": True, "action": action, "policies": policies,
                        "count": len(policies), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── CASCADE (CASC-001) ─────────────────────────────────────────────────
        elif action == "cascade.run":
            try:
                from neocortex.core.cascade_consolidator import run_cascade
                hours = timeout if timeout else 24
                result = run_cascade(hours=hours)
                return {"success": True, "action": action, **result}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cascade.status":
            try:
                from neocortex.core.cascade_consolidator import cascade_status
                return {"success": True, "action": action, **cascade_status()}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}
        # ORBITAL BRIDGE
        _orbital_result = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("orbital_bridge", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _orbital_result = _mod.orbital_dispatch(action, root)
        except Exception: pass
        if _orbital_result is not None: return _orbital_result



        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["task.execute", "task.list", "task.cancel", "task.status",
                                  "agent.spawn", "agent.heartbeat", "agent.consume", "agent.list",
                                  "agent.list_ephemeral", "task.get_result",
                                  "dispatch.create", "dispatch.status",
                                  "workers.spawn", "workers.status",
                                  "policy.check", "policy.list",
                                  "cascade.run", "cascade.status"],
                    "timestamp": ts}
