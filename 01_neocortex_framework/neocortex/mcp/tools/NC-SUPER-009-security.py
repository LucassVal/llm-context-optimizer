#!/usr/bin/env python3
"""
NC-SUPER-009 — neocortex_security
FÓRUM — Segurança e Hooks

Funde: security (026), hooks (034).

Actions:
  access.validate, lock.check, lock.list
  hook.register, hook.trigger, hook.list, hook.remove
  audit.log_event
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_security"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


# In-memory hook registry
_HOOKS: Dict[str, list] = {}


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_security(
        action: str,
        resource: str = "",
        agent_role: str = "T0",
        lock_path: str = "",
        hook_name: str = "",
        hook_event: str = "",
        hook_action: str = "",
        event_type: str = "",
        event_details: str = "",
        auth_token: str = "",
    ) -> Dict[str, Any]:
        """FÓRUM — Segurança, Locks e Hooks.
        Funde: security (026) + hooks (034).
        Actions: access.validate, lock.check, lock.list,
                 hook.register, hook.trigger, hook.list, hook.remove,
                 audit.log_event, auth.issue_token
        """
        ts = _ts()
        root = _root()

        # ── ACCESS ────────────────────────────────────────────────────────────
        if action == "access.validate":
            # ZERO-TRUST: CryptoHub Interceptor
            import importlib.util
            crypto_path = root / "01_neocortex_framework" / "neocortex" / "core" / "services" / "NC-SVC-FR-017-crypto-hub.py"
            spec = importlib.util.spec_from_file_location("crypto_hub", crypto_path)
            ch_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ch_mod)
            hub = ch_mod.CryptoHub()

            restricted = ["atomic_locks", "server.py", "sub_server.py", "NC-NAM-FR-001"]
            is_restricted = any(r in resource for r in restricted)
            
            if is_restricted:
                if not auth_token:
                    return {"success": False, "allowed": False, "reason": "RESTRICTED_ZERO_TRUST (Missing auth_token)", "timestamp": ts}
                
                dec = hub.decrypt(auth_token)
                if not dec.success:
                    return {"success": False, "allowed": False, "reason": f"INVALID_TOKEN: {dec.error}", "timestamp": ts}
                
                # Payload format: role=T0|issued=YYYY-MM-DD...
                if "role=T0" not in dec.plaintext:
                    return {"success": False, "allowed": False, "reason": "INSUFFICIENT_PRIVILEGES_ZERO_TRUST", "timestamp": ts}

            return {"success": True, "action": action, "resource": resource,
                    "agent_role": agent_role, "allowed": True,
                    "reason": "OK_ZERO_TRUST", "timestamp": ts}
        
        elif action == "auth.issue_token":
            if agent_role.upper() != "T0":
                return {"success": False, "error": "Apenas T0 pode emitir tokens na root", "timestamp": ts}
            import importlib.util
            crypto_path = root / "01_neocortex_framework" / "neocortex" / "core" / "services" / "NC-SVC-FR-017-crypto-hub.py"
            spec = importlib.util.spec_from_file_location("crypto_hub", crypto_path)
            ch_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ch_mod)
            hub = ch_mod.CryptoHub()
            
            payload = f"role={agent_role.upper()}|resource={resource}|issued={ts}"
            res = hub.encrypt(payload)
            if not res.success:
                return {"success": False, "error": "CryptoHub fail - master key indisponível", "timestamp": ts}
            return {"success": True, "action": action, "token": res.token, "token_hash": res.token_hash, "payload": payload, "timestamp": ts}

        elif action == "lock.check":
            if not lock_path:
                return {"success": False, "error": "lock_path obrigatório", "timestamp": ts}
            locks_file = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
            if not locks_file.exists():
                return {"success": True, "action": action, "locked": False,
                        "note": "locks file não encontrado", "timestamp": ts}
            content = locks_file.read_text(encoding="utf-8")
            is_locked = lock_path in content
            return {"success": True, "action": action, "path": lock_path,
                    "locked": is_locked, "timestamp": ts}

        elif action == "lock.list":
            locks_file = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
            if not locks_file.exists():
                return {"success": True, "action": action, "locks": [], "timestamp": ts}
            try:
                import yaml
                data = yaml.safe_load(locks_file.read_text(encoding="utf-8"))
                locks = data.get("locked_files", []) if isinstance(data, dict) else []
                return {"success": True, "action": action, "locks": locks,
                        "count": len(locks), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── HOOKS ─────────────────────────────────────────────────────────────
        elif action == "hook.register":
            if not hook_name or not hook_event:
                return {"success": False, "error": "hook_name e hook_event obrigatórios", "timestamp": ts}
            if hook_event not in _HOOKS:
                _HOOKS[hook_event] = []
            _HOOKS[hook_event].append({"name": hook_name, "action": hook_action, "registered": ts})
            return {"success": True, "action": action, "hook": hook_name,
                    "event": hook_event, "registered": ts, "timestamp": ts}

        elif action == "hook.trigger":
            if not hook_event:
                return {"success": False, "error": "hook_event obrigatório", "timestamp": ts}
            triggered = _HOOKS.get(hook_event, [])
            return {"success": True, "action": action, "event": hook_event,
                    "hooks_triggered": len(triggered), "hooks": triggered, "timestamp": ts}

        elif action == "hook.list":
            all_hooks = {event: hooks for event, hooks in _HOOKS.items()}
            total = sum(len(v) for v in all_hooks.values())
            return {"success": True, "action": action, "hooks_by_event": all_hooks,
                    "total": total, "timestamp": ts}

        elif action == "hook.remove":
            if not hook_name:
                return {"success": False, "error": "hook_name obrigatório", "timestamp": ts}
            removed = 0
            for event in list(_HOOKS.keys()):
                before = len(_HOOKS[event])
                _HOOKS[event] = [h for h in _HOOKS[event] if h["name"] != hook_name]
                removed += before - len(_HOOKS[event])
            return {"success": True, "action": action, "hook": hook_name,
                    "removed": removed, "timestamp": ts}

        # ── AUDIT LOG ─────────────────────────────────────────────────────────
        elif action == "audit.log_event":
            if not event_type:
                return {"success": False, "error": "event_type obrigatório", "timestamp": ts}
            log_dir = root / "DIR-DS-002-audit-logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            entry = {"timestamp": ts, "event_type": event_type,
                     "agent": agent_role, "details": event_details}
            log_file = log_dir / f"NC-EVT-{ts.replace(':', '-')}.json"
            log_file.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"success": True, "action": action, "logged": str(log_file),
                    "event_type": event_type, "timestamp": ts}


        elif action == "gateway.status":
            import socket
            try:
                s = socket.create_connection(("localhost", 18790), timeout=1); s.close()
                return {"success": True, "action": action, "picoclaw": {"port": 18790, "reachable": True}, "timestamp": ts}
            except:
                return {"success": True, "action": action, "picoclaw": {"port": 18790, "reachable": False}, "timestamp": ts}

        # ── CIRCUIT BREAKER (SEC-403) ──────────────────────────────────────────
        elif action == "cb.status":
            try:
                from neocortex.core.circuit_breaker import (
                    get_circuit_breaker,
                    list_breakers,
                )
                if resource:
                    cb = get_circuit_breaker(resource)
                    return {"success": True, "action": action, "breaker": cb.status(), "timestamp": ts}
                return {"success": True, "action": action, "breakers": list_breakers(), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cb.reset":
            if not resource:
                return {"success": False, "error": "resource (agent_id) obrigatório", "timestamp": ts}
            if agent_role.upper() != "T0":
                return {"success": False, "error": "cb.reset requer agent_role=T0", "timestamp": ts}
            try:
                from neocortex.core.circuit_breaker import reset_breaker
                ok = reset_breaker(resource)
                return {"success": ok, "action": action, "agent_id": resource,
                        "reset": ok, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cb.list":
            try:
                from neocortex.core.circuit_breaker import list_breakers
                breakers = list_breakers()
                summary = [{
                    "agent_id": aid,
                    "state": s["state"],
                    "calls_in_window": s["calls_in_window"],
                    "total_blocked": s["total_blocked"],
                } for aid, s in breakers.items()]
                open_count = sum(1 for s in summary if s["state"] == "OPEN")
                return {"success": True, "action": action, "breakers": summary,
                        "total": len(summary), "open_count": open_count, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cb.record":
            if not resource:
                return {"success": False, "error": "resource (agent_id) obrigatório", "timestamp": ts}
            try:
                from neocortex.core.circuit_breaker import (
                    CircuitBreakerError,
                    get_circuit_breaker,
                )
                cb = get_circuit_breaker(resource)
                cb.record_call(event_details)
                return {"success": True, "action": action, "agent_id": resource,
                        "state": cb.state.value, "timestamp": ts}
            except CircuitBreakerError as e:
                return {"success": False, "action": action, "blocked": True,
                        "reason": str(e), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["access.validate", "auth.issue_token", "lock.check", "lock.list",
                                  "hook.register", "hook.trigger", "hook.list", "hook.remove",
                                  "audit.log_event", "gateway.status",
                                  "cb.status", "cb.reset", "cb.list", "cb.record"],
                    "timestamp": ts}

