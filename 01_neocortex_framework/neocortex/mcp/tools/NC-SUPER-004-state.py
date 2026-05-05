#!/usr/bin/env python3
"""---
NC-SUPER-004 — neocortex_state
---
"""

"""---
NC-SUPER-004 — neocortex_state
---
"""

"""
NC-SUPER-004 — neocortex_state
CORTE TJ — Estado e Persistência

Funde: checkpoint (004), regression (016), savepoint (031),
       session (022), ledger (010).

Actions:
  checkpoint.get, checkpoint.set, checkpoint.list
  regression.check, regression.baseline
  savepoint.create, savepoint.list, savepoint.rollback
  session.start, session.end, session.status, session.heartbeat
  ledger.read, ledger.update, ledger.stats
"""
import contextlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_state"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_state(
        action: str,
        checkpoint_key: str = "",
        checkpoint_data: str = "",
        savepoint_name: str = "",
        session_id: str = "",
        summary: str = "",
        limit: int = 10,
    ) -> dict[str, Any]:
        """CORTE TJ — Estado e Persistência.
        Funde: checkpoint, regression, savepoint, session, ledger.
        Actions: checkpoint.get/set/list, regression.check/baseline,
                 savepoint.create/list/rollback, session.start/end/status/heartbeat,
                 ledger.read/update/stats
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

        # ── TOOLGUARD: STEP 0 + LockGuard (G1+G2+G3) ─────────────────────────
        _guard = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("tool_guard", str(_root() / "neocortex" / "core" / "NC-CORE-FR-125-tool-guard.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _guard = _mod.ToolGuard()

            # STEP 0 regression check
            _step0 = _guard.step_zero(action)
            if not _step0.get("ok"):
                return {"success": True, "action": action,
                        "step0_warning": _step0.get("warning", "STEP-0 alert"),
                        "matched_error": _step0.get("matched_error", ""), "timestamp": ts}
        except Exception:
            pass

        # ── CHECKPOINT ────────────────────────────────────────────────────────
        if action == "checkpoint.get":
            try:
                from neocortex.core import get_checkpoint_service
                svc = get_checkpoint_service()
                if checkpoint_key:
                    # Get specific checkpoint from timeline
                    result = svc.get_current_checkpoint()
                    if result.get("checkpoint_id") == checkpoint_key:
                        data = result
                    else:
                        # Try to find in timeline
                        history = svc.list_checkpoint_history(limit=100)
                        for event in history.get("history", []):
                            if event.get("checkpoint_id") == checkpoint_key:
                                data = event
                                break
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": True, "action": action, "data": data, "timestamp": ts}

        elif action == "checkpoint.set":
            if not checkpoint_key:
                return {"success": False, "error": "checkpoint_key obrigatório", "timestamp": ts}
            # G1 LockGuard: validate write to ledger
            if _guard:
                _ok = _guard.validate_write(
                    "DIR-CORE-FR-001-core-central/NC-LED-FR-001-framework-ledger.json")
                if not _ok:
                    return {"success": False, "error": _guard.last_error, "timestamp": ts}
                # G3 STEP -1: auto savepoint before write
                _guard.savepoint_before_write("checkpoint.set")
            try:
                from neocortex.core import get_checkpoint_service
                svc = get_checkpoint_service()
                result = svc.set_current_checkpoint(
                    checkpoint_id=checkpoint_key,
                    description=checkpoint_data[:100] if checkpoint_data else f"Checkpoint {checkpoint_key}"
                )
                return {"success": True, "action": action, "key": checkpoint_key,
                        "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "checkpoint.list":
            try:
                from neocortex.core import get_checkpoint_service
                svc = get_checkpoint_service()
                history = svc.list_checkpoint_history(limit=limit)
                checkpoints = [event for event in history.get("history", []) if event.get("event") == "checkpoint_set"]
                return {"success": True, "action": action, "checkpoints": checkpoints,
                        "count": len(checkpoints), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── REGRESSION ────────────────────────────────────────────────────────
        elif action == "regression.check":
            try:
                from neocortex.core import get_regression_service
                svc = get_regression_service()
                result = svc.check()
                return {"success": True, "action": action, "regression_status": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "regression.baseline":
            try:
                from neocortex.core import get_regression_service
                svc = get_regression_service()
                result = svc.set_baseline()
                return {"success": True, "action": action, "baseline_set": True,
                        "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── SAVEPOINT ───────────────────────────────────────────────────
        elif action == "savepoint.create":
            name = savepoint_name or f"sp_{ts.replace(':', '-')}"
            sp_dir = _root() / "01_neocortex_framework" / ".neocortex" / "savepoints"
            sp_dir.mkdir(parents=True, exist_ok=True)
            # 1. Tentar via service
            svc_ok = False
            try:
                from neocortex.core import get_savepoint_service
                svc = get_savepoint_service()
                result = svc.create(name=name, summary=summary)
                svc_ok = True
            except Exception:
                result = {}
            # 2. Snapshot filesystem real (SEMPRE)
            import json as _json
            snapshot = {
                "name": name,
                "summary": summary or "checkpoint",
                "created": ts,
                "files_snapshot": {},
            }
            # Capturar ledger + cortex
            for snap_file in [
                _root() / "01_neocortex_framework" / ".neocortex" / "ledger.json",
                _root() / "01_neocortex_framework" / ".neocortex" / "cortex.json",
                _root() / "01_neocortex_framework" / ".neocortex" / "guardian_state.json",
            ]:
                if snap_file.exists():
                    with contextlib.suppress(Exception):
                        snapshot["files_snapshot"][snap_file.name] = snap_file.read_text("utf-8")[:8000]
            sp_file = sp_dir / f"{name}.json"
            sp_file.write_text(_json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"success": True, "action": action, "savepoint": name,
                    "snapshot_file": str(sp_file),
                    "files_captured": list(snapshot["files_snapshot"].keys()),
                    "svc_ok": svc_ok, "timestamp": ts}

        elif action == "savepoint.list":
            sp_dir = _root() / "01_neocortex_framework" / ".neocortex" / "savepoints"
            if not sp_dir.exists():
                return {"success": True, "action": action, "savepoints": [], "count": 0, "timestamp": ts}
            savepoints = sorted(
                [{"name": f.stem, "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                  "size_kb": round(f.stat().st_size / 1024, 1)}
                 for f in sp_dir.glob("*.json")],
                key=lambda x: x["created"], reverse=True
            )
            return {"success": True, "action": action, "savepoints": savepoints[:limit],
                    "count": len(savepoints), "timestamp": ts}

        elif action == "savepoint.rollback":
            """P4 (SEC-402): Rollback real — restaura arquivos do snapshot."""
            if not savepoint_name:
                return {"success": False, "error": "savepoint_name obrigatório", "timestamp": ts}
            import json as _json
            sp_dir = _root() / "01_neocortex_framework" / ".neocortex" / "savepoints"
            sp_file = sp_dir / f"{savepoint_name}.json"
            if not sp_file.exists():
                return {"success": False, "action": action,
                        "error": f"Savepoint '{savepoint_name}' não encontrado",
                        "available": [f.stem for f in sp_dir.glob("*.json")] if sp_dir.exists() else [],
                        "timestamp": ts}
            try:
                snapshot = _json.loads(sp_file.read_text("utf-8"))
                restored = []
                errors   = []
                neocortex_dir = _root() / "01_neocortex_framework" / ".neocortex"
                for filename, content in snapshot.get("files_snapshot", {}).items():
                    target = neocortex_dir / filename
                    try:
                        # Backup antes de restaurar
                        if target.exists():
                            bak = target.with_suffix(f".bak_{ts.replace(':', '-')}.json")
                            bak.write_text(target.read_text("utf-8"), encoding="utf-8")
                        target.write_text(content, encoding="utf-8")
                        restored.append(filename)
                    except Exception as ex:
                        errors.append(f"{filename}: {ex}")
                return {"success": True, "action": action,
                        "rolled_back_to": savepoint_name,
                        "created_at": snapshot.get("created"),
                        "summary": snapshot.get("summary"),
                        "restored_files": restored,
                        "errors": errors, "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        elif action == "savepoint.diff":
            """Compara estado atual vs snapshot para auditoria pré-rollback."""
            if not savepoint_name:
                return {"success": False, "error": "savepoint_name obrigatório", "timestamp": ts}
            import json as _json
            sp_dir = _root() / "01_neocortex_framework" / ".neocortex" / "savepoints"
            sp_file = sp_dir / f"{savepoint_name}.json"
            if not sp_file.exists():
                return {"success": False, "action": action,
                        "error": f"Savepoint '{savepoint_name}' não encontrado", "timestamp": ts}
            snapshot = _json.loads(sp_file.read_text("utf-8"))
            diff = {"savepoint": savepoint_name, "created_at": snapshot.get("created"), "files": {}}
            neocortex_dir = _root() / "01_neocortex_framework" / ".neocortex"
            for filename in snapshot.get("files_snapshot", {}):
                current_file = neocortex_dir / filename
                diff["files"][filename] = {
                    "in_snapshot": True,
                    "current_exists": current_file.exists(),
                    "current_size": current_file.stat().st_size if current_file.exists() else 0,
                    "snapshot_size": len(snapshot["files_snapshot"][filename]),
                }
            return {"success": True, "action": action, "diff": diff, "timestamp": ts}

        # ── SESSION ───────────────────────────────────────────────────────────
        elif action == "session.start":
            try:
                session_manager = None  # R26 orbital: no server.py dependency
                if session_manager is not None:
                    session_manager.start(session_id=session_id or f"sess_{ts.replace(':', '-')}")
                    return {"success": True, "action": action,
                            "session_active": session_manager.active,
                            "session_id": session_id or session_manager.session_id,
                            "session_start": session_manager.session_start,
                            "timestamp": ts}
                return {"success": True, "action": action, "session_active": True,
                        "session_id": session_id or f"sess_{ts.replace(':', '-')}",
                        "session_start": ts,
                        "note": "SessionManager desabilitado — pass-through", "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action, "session_active": True,
                        "session_start": ts,
                        "note": f"Pass-through ({e})", "timestamp": ts}

        elif action == "session.status":
            try:
                session_manager = None  # R26 orbital: no server.py dependency
                if session_manager is not None:
                    return {"success": True, "action": action,
                            "session_active": session_manager.active,
                            "session_start": session_manager.session_start,
                            "last_heartbeat": session_manager.last_heartbeat,
                            "timestamp": ts}
                return {"success": True, "action": action,
                        "session_active": False,
                        "note": "SessionManager desabilitado", "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action, "note": str(e), "timestamp": ts}

        elif action == "session.heartbeat":
            try:
                session_manager = None  # R26 orbital: no server.py dependency
                if session_manager is not None:
                    result = session_manager.heartbeat()
                    return {"success": True, "action": action, "heartbeat": result, "timestamp": ts}
                return {"success": True, "action": action, "heartbeat": ts,
                        "note": "SessionManager desabilitado — pass-through", "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action, "heartbeat": ts,
                        "note": f"Pass-through ({e})", "timestamp": ts}

        elif action == "session.end":
            try:
                import importlib.util
                from pathlib import Path as _Path
                _root_p = _Path(__file__).parents[4]
                _svc_file = _root_p / "01_neocortex_framework" / "neocortex" / "core" / "services" / "NC-SVC-FR-021-session-memory-writer.py"
                _spec = importlib.util.spec_from_file_location("session_memory_writer", _svc_file)
                _mod = importlib.util.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)
                sw = _mod.SessionMemoryWriter()
                result = sw.session_end(summary=summary or "Sessão encerrada")
                return {"success": True, "action": action, "session_end": result, "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action,
                        "note": f"SessionMemoryWriter: {e}", "timestamp": ts}

        # ── LEDGER ────────────────────────────────────────────────────────────
        elif action == "ledger.read":
            try:
                from neocortex.core.file_utils import read_ledger
                data = read_ledger()
                return {"success": True, "action": action, "ledger": data, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "ledger.update":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                result = svc.update_session_metrics(interaction_type=summary or "manual", tokens_used=0)
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


        elif action == "regression.add_entry":
            if not content:
                return {"success": False, "error": "content obrigatorio", "timestamp": ts}
            try:
                from neocortex.core import get_regression_service
                svc = get_regression_service()
                result = svc.add_entry(content) if hasattr(svc, "add_entry") else {"error": "add_entry nao disponivel"}
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "regression.list_all":
            try:
                from neocortex.core import get_regression_service
                svc = get_regression_service()
                result = svc.list_all() if hasattr(svc, "list_all") else {"entries": []}
                return {"success": True, "action": action, "entries": result.get("entries", []), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}
        # ── ORBITAL BRIDGE: delegar ações ──────────────────────────────────
        _orbital_result = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("orbital_bridge", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _orbital_result = _mod.orbital_dispatch(action, root)
        except Exception:
            pass
        if _orbital_result is not None:
            return _orbital_result

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["checkpoint.get", "checkpoint.set", "checkpoint.list",
                                  "regression.check", "regression.baseline",
                                  "savepoint.create", "savepoint.list", "savepoint.rollback",
                                  "session.start", "session.status", "session.heartbeat", "session.end",
                                  "ledger.read", "ledger.update", "ledger.stats"],
                    "timestamp": ts}
