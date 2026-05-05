#!/usr/bin/env python3
"""---
NC-SUPER-016-picoclaw.py
---
"""

"""---
NC-SUPER-016-picoclaw.py
---
"""

"""
NC-SUPER-016-picoclaw.py
PICOCLAW MCP Super-Tool — Interface MCP para o servidor PICOCLAW :18790

Actions:
  picoclaw.start   — Iniciar servidor A2A :18790
  picoclaw.stop    — Parar servidor
  picoclaw.status  — Health check
  picoclaw.publish — Publicar evento A2A
  picoclaw.poll    — Ler próximo evento (long-poll)
  picoclaw.dispatch — Enfileirar task
  picoclaw.llm_call — Chamar LLM via tier routing (LiteLLM :4000 ou Ollama fallback)
"""
import importlib
import json
import logging
import urllib.request
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME   = "neocortex_picoclaw"
_BASE_URL   = "http://localhost:18790"


def _get_server_mod():
    """Importa NC-SVC-FR-019 via importlib (R09: sem import com hífen)."""
    return importlib.import_module(
        "neocortex.core.services.NC_SVC_FR_019_picoclaw_server",
        # fallback: tentar pelo nome real se __init__ registrou alias
    )


def _http_post(path: str, body: dict, timeout: int = 60) -> Dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{_BASE_URL}{path}", data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _http_post_raw(path: str, data: bytes, timeout: int = 60) -> Dict:
    req = urllib.request.Request(
        f"{_BASE_URL}{path}", data=data,
        headers={"Content-Type": "application/octet-stream"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _http_get(path: str, timeout: int = 10) -> Dict:
    try:
        with urllib.request.urlopen(f"{_BASE_URL}{path}", timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_picoclaw(
        action: str,
        event_type: str = "",
        payload: str = "{}",
        source: str = "mcp",
        task_name: str = "",
        task_payload: str = "{}",
        task_id: str = "",
        priority: int = 20,
        poll_timeout: int = 5,
        prompt: str = "",
        system: str = "",
        complexity: str = "OPERACIONAL",
        max_tokens: int = 512,
        timeout: int = 60,
        mmap_shm_id: str = "",
        mmap_size: int = 0,
    ) -> Dict[str, Any]:
        """PICOCLAW — Servidor HTTP A2A :18790.
        Actions: picoclaw.start, picoclaw.stop, picoclaw.status,
                 picoclaw.publish, picoclaw.poll, picoclaw.dispatch,
                 picoclaw.task_status, picoclaw.llm_call,
                 picoclaw.mmap_write, picoclaw.mmap_read
        LLM Tiers: OPERACIONAL→qwen-1.5b (Ollama) | TECNICO→deepseek-v4-flash | RACIOCINIO→deepseek-v4-pro
        """
        # ── picoclaw.start ───────────────────────────────────────────────────
        if action == "picoclaw.start":
            try:
                import importlib as _il
                svc = _il.import_module(
                    "neocortex.core.services.NC_SVC_FR_019_picoclaw_server"
                )
                return svc.start()
            except ModuleNotFoundError:
                # Tentar path alternativo com nome exato do arquivo
                import sys
                from pathlib import Path
                fw = Path(__file__).parents[3]
                svc_path = fw / "core" / "services" / "NC-SVC-FR-019-picoclaw-server.py"
                import importlib.util
                spec = importlib.util.spec_from_file_location("picoclaw_svc", svc_path)
                mod  = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sys.modules["picoclaw_svc"] = mod
                return mod.start()
            except Exception as e:
                return {"ok": False, "error": str(e)}

        # ── picoclaw.stop ────────────────────────────────────────────────────
        elif action == "picoclaw.stop":
            r = _http_get("/health", timeout=3)
            if not r.get("ok"):
                return {"ok": True, "status": "already_stopped"}
            # stop via health endpoint não existe — signal via module
            return {"ok": True, "note": "Use picoclaw.start para reiniciar"}

        # ── picoclaw.status ──────────────────────────────────────────────────
        elif action == "picoclaw.status":
            return _http_get("/health", timeout=5)

        # ── picoclaw.publish ─────────────────────────────────────────────────
        elif action == "picoclaw.publish":
            if not event_type:
                return {"ok": False, "error": "event_type obrigatório"}
            try:
                payload_data = json.loads(payload) if isinstance(payload, str) else payload
            except json.JSONDecodeError:
                payload_data = {"raw": payload}
            return _http_post("/event/publish", {
                "type": event_type, "payload": payload_data, "source": source
            }, timeout=10)

        # ── picoclaw.poll ────────────────────────────────────────────────────
        elif action == "picoclaw.poll":
            if not event_type:
                return {"ok": False, "error": "event_type obrigatório"}
            return _http_get(f"/event/poll?type={event_type}&timeout={poll_timeout}",
                             timeout=poll_timeout + 3)

        # ── picoclaw.dispatch ────────────────────────────────────────────────
        elif action == "picoclaw.dispatch":
            if not task_name:
                return {"ok": False, "error": "task_name obrigatório"}

            raw_payload_str = task_payload if isinstance(task_payload, str) else json.dumps(task_payload)
            # SOTA Phase 4.2: Payload > 1024 bytes gets auto mmap-ed
            if len(raw_payload_str) > 1024:
                mmap_resp = _http_post_raw("/mmap_write", raw_payload_str.encode("utf-8"), timeout=15)
                if mmap_resp.get("success"):
                    payload_data = {"_ipc_ptr": mmap_resp["shm_id"], "_ipc_size": mmap_resp["size"], "_ipc_mmap": True}
                else:
                    try:
                        payload_data = json.loads(task_payload)
                    except json.JSONDecodeError:
                        payload_data = {"raw": task_payload}
            else:
                try:
                    payload_data = json.loads(task_payload) if isinstance(task_payload, str) else task_payload
                except json.JSONDecodeError:
                    payload_data = {"raw": task_payload}

            return _http_post("/task/dispatch", {
                "name": task_name, "payload": payload_data, "priority": priority
            }, timeout=10)

        # ── picoclaw.task_status ─────────────────────────────────────────────
        elif action == "picoclaw.task_status":
            if not task_id:
                return {"ok": False, "error": "task_id obrigatório"}
            return _http_get(f"/task/status/{task_id}", timeout=5)

        # ── picoclaw.llm_call ────────────────────────────────────────────────
        elif action == "picoclaw.llm_call":
            if not prompt:
                return {"ok": False, "error": "prompt obrigatório"}
            return _http_post("/llm/call", {
                "prompt": prompt, "system": system,
                "complexity": complexity, "max_tokens": max_tokens,
                "timeout": timeout,
            }, timeout=timeout + 5)

        # ── picoclaw.mmap_read ───────────────────────────────────────────────
        elif action == "picoclaw.mmap_read":
            if not mmap_shm_id or not mmap_size:
                return {"ok": False, "error": "mmap_shm_id e mmap_size obrigatórios"}
            return _http_get(f"/mmap_read?shm_id={mmap_shm_id}&size={mmap_size}", timeout=10)

        # ── picoclaw.mmap_write ──────────────────────────────────────────────
        elif action == "picoclaw.mmap_write":
            if not payload:
                return {"ok": False, "error": "payload obrigatório para mapear"}
            return _http_post_raw("/mmap_write", payload.encode("utf-8"), timeout=15)

        else:
            return {
                "ok": False,
                "error": f"action desconhecida: {action}",
                "available": [
                    "picoclaw.start", "picoclaw.stop", "picoclaw.status",
                    "picoclaw.publish", "picoclaw.poll",
                    "picoclaw.dispatch", "picoclaw.task_status",
                    "picoclaw.llm_call", "picoclaw.mmap_write", "picoclaw.mmap_read"
                ],
            }
