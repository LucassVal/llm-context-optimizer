#!/usr/bin/env python3
"""
NC-SUPER-014 — neocortex_ledger
FÓRUM — Ledger + Agent Identity

Funde: ledger (010), agent (002) identity parts.

Actions:
  ledger.read, ledger.write, ledger.stats, ledger.metrics
  agent.register, agent.identity, agent.token_budget
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_ledger"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_ledger(
        action: str,
        agent_id: str = "",
        agent_role: str = "T0",
        interaction_type: str = "manual",
        tokens_used: int = 0,
        detail_key: str = "",
    ) -> Dict[str, Any]:
        """FÓRUM — Ledger e Agent Identity.
        Actions: ledger.read, ledger.write, ledger.stats, ledger.metrics,
                 agent.register, agent.identity, agent.token_budget
        """
        ts = _ts()

        if action == "ledger.read":
            try:
                from neocortex.core.file_utils import read_ledger
                data = read_ledger()
                if detail_key and isinstance(data, dict):
                    return {"success": True, "action": action, "key": detail_key,
                            "value": data.get(detail_key), "timestamp": ts}
                return {"success": True, "action": action, "ledger": data, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "ledger.write":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                result = svc.update_session_metrics(interaction_type=interaction_type,
                                                    tokens_used=tokens_used)
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "ledger.stats":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                stats = svc.get_stats() if hasattr(svc, "get_stats") else svc.read()
                return {"success": True, "action": action, "stats": stats, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "ledger.metrics":
            try:
                from neocortex.mcp.server import get_metrics_store
                ms = get_metrics_store()
                if ms:
                    metrics = ms.get_all()
                    return {"success": True, "action": action, "metrics": metrics, "timestamp": ts}
                return {"success": True, "action": action, "metrics": {},
                        "note": "MetricsStore indisponível", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "agent.register":
            if not agent_id:
                return {"success": False, "error": "agent_id obrigatório", "timestamp": ts}
            reg_dir = _root() / "DIR-DS-002-audit-logs"
            reg_dir.mkdir(parents=True, exist_ok=True)
            entry = {"agent_id": agent_id, "role": agent_role, "registered": ts}
            (reg_dir / f"NC-AGT-{agent_id}.json").write_text(
                json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
            return {"success": True, "action": action, "agent_id": agent_id,
                    "role": agent_role, "timestamp": ts}

        elif action == "agent.identity":
            return {"success": True, "action": action,
                    "identity": {"id": agent_id or "T0-Antigravity",
                                 "role": agent_role,
                                 "cf_version": "CF-v0.2",
                                 "authority": {"T0": "PLENA", "T2": "OPERACIONAL"}.get(agent_role, "RESTRITA")},
                    "timestamp": ts}

        elif action == "agent.token_budget":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                data = svc.read()
                tokens = data.get("total_tokens_used", 0) if isinstance(data, dict) else 0
                budget = 100000
                return {"success": True, "action": action,
                        "tokens_used": tokens,
                        "budget": budget,
                        "remaining": budget - tokens,
                        "pct_used": round(tokens / budget * 100, 1),
                        "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["ledger.read", "ledger.write", "ledger.stats", "ledger.metrics",
                                  "agent.register", "agent.identity", "agent.token_budget"],
                    "timestamp": ts}
