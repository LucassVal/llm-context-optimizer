#!/usr/bin/env python3
"""---
NC-TOOL-FR-020 — openclaude_bridge
---
"""

"""---
NC-TOOL-FR-020 — openclaude_bridge
---
"""

"""
NC-TOOL-FR-020 — openclaude_bridge
Bridge MCP NeoCortex ↔ OpenClaude (Antigravity/T0)

Expõe controle do OpenClaude como ferramentas MCP:
  - session.status — verifica se o OpenClaude está ativo e conectado
  - session.sync — força sincronização de memória entre NeoCortex e OpenClaude
  - session.prompt — envia um prompt direto para o OpenClaude via gateway
  - tools.list — lista as ferramentas que o OpenClaude está consumindo do MCP
  - gateway.health — health check do gateway DeepSeek (:4001)

Integra:
  - Gateway DeepSeek :4001 (NC-SVC-FR-102)
  - MCP Server :8765 (NC-SVC-FR-100)
  - OpenClaude profile (.openclaude-profile.json)
"""
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# NeoCortex Imports
from neocortex.infra.llm.NC_SVC_FR_026_profile_router import ProfileRouter

logger = logging.getLogger(__name__)
TOOL_NAME = "openclaude_bridge"

GATEWAY_URL = "http://localhost:4001"
MCP_URL = "http://localhost:8765"
OPENCLAUDE_PROFILE = Path(
    os.environ.get(
        "OPENCLAUDE_PROFILE",
        r"C:\Users\Lucas Valério\.gemini\antigravity\brain\.openclaude-profile.json"
    )
)
GATEWAY_HEALTH_ENDPOINT = f"{GATEWAY_URL}/health"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _http_get(url: str, timeout: int = 5) -> Dict:
    """GET request simples com stdlib."""
    try:
        import urllib.request
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return {"ok": resp.status == 200, "status": resp.status, "data": json.loads(body)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _profile_status() -> Dict:
    """Lê o profile do OpenClaude e retorna status."""
    if not OPENCLAUDE_PROFILE.exists():
        return {"exists": False, "error": "Profile não encontrado"}
    try:
        data = json.loads(OPENCLAUDE_PROFILE.read_text(encoding="utf-8"))
        return {
            "exists": True,
            "provider": data.get("provider", "unknown"),
            "api_base": data.get("api_base", "unknown"),
            "model": data.get("model", "unknown"),
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def _gateway_health() -> Dict:
    """Health check no gateway DeepSeek :4001."""
    result = _http_get(GATEWAY_HEALTH_ENDPOINT, timeout=5)
    if result.get("ok"):
        return {"online": True, "model": result["data"].get("model", "unknown")}
    return {"online": False, "error": result.get("error", "Gateway offline")}


def _mcp_health() -> Dict:
    """Health check no MCP Server :8765."""
    result = _http_get(f"{MCP_URL}/health", timeout=5)
    if result.get("ok"):
        return {"online": True, "tools_loaded": result["data"].get("tools_loaded", 0)}
    # SSE endpoint não tem /health, tentar SSE como fallback
    try:
        import urllib.request
        req = urllib.request.Request(f"{MCP_URL}/sse")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                return {"online": True, "transport": "sse"}
    except Exception:
        pass
    return {"online": False, "error": result.get("error", "MCP Server offline")}


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def openclaude_bridge(
        action: str,
        prompt_text: str = "",
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Bridge MCP NeoCortex ↔ OpenClaude (Antigravity/T0).

        Actions:
          session.status    — Status da conexão OpenClaude + Gateway + MCP
          session.sync      — Sincroniza memória entre NeoCortex e OpenClaude
          session.prompt    — Envia prompt ao OpenClaude via gateway DeepSeek
          gateway.health    — Health check do gateway :4001
          mcp.status        — Status do servidor MCP :8765
          profile.status    — Status do profile OpenClaude
        """
        ts = _ts()


        # UBL Gateway (Kernel 0)
        try:
            from neocortex.core.utils.NC_UTL_FR_004_gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok: return _report
        except Exception: pass
        if action == "session.status":
            gw = _gateway_health()
            mcp_st = _mcp_health()
            prof = _profile_status()
            return {
                "success": True,
                "action": action,
                "timestamp": ts,
                "gateway": gw,
                "mcp_server": mcp_st,
                "openclaude_profile": prof,
                "overall": "ONLINE" if gw.get("online") else "DEGRADED",
            }

        elif action == "gateway.health":
            gw = _gateway_health()
            return {
                "success": gw.get("online", False),
                "action": action,
                "timestamp": ts,
                **gw,
            }

        elif action == "mcp.status":
            mcp_st = _mcp_health()
            return {
                "success": mcp_st.get("online", False),
                "action": action,
                "timestamp": ts,
                **mcp_st,
            }

        elif action == "profile.status":
            prof = _profile_status()
            return {
                "success": prof.get("exists", False),
                "action": action,
                "timestamp": ts,
                **prof,
            }

        elif action == "config.view":
            """Mostra a configuração atual do Claude Code via CLI."""
            try:
                # Tenta rodar claude config ou similar
                # Como claude code é interativo, tentamos capturar a versão e o profile
                res = subprocess.run(["openclaude", "--version"], capture_output=True, text=True, timeout=5)
                version = res.stdout.strip()
                prof = _profile_status()
                return {
                    "success": True,
                    "action": action,
                    "version": version,
                    "profile": prof,
                    "timestamp": ts,
                    "message": "Configuração básica extraída do profile e CLI."
                }
            except Exception as e:
                return {"success": False, "action": action, "error": str(e)}

        elif action == "session.list":
            """Lista sessões locais do Claude Code."""
            sessions_dir = Path(r"C:\Users\Lucas Valério\.claude\sessions")
            sessions = []
            if sessions_dir.exists():
                for f in sessions_dir.glob("*.json"):
                    try:
                        data = json.loads(f.read_text(encoding="utf-8"))
                        sessions.append({
                            "id": data.get("sessionId"),
                            "pid": data.get("pid"),
                            "started_at": data.get("startedAt"),
                            "file": f.name
                        })
                    except:
                        pass
            return {
                "success": True,
                "action": action,
                "count": len(sessions),
                "sessions": sessions,
                "timestamp": ts
            }

        elif action == "agent.doctor":
            """Diagnóstico completo do ambiente OpenClaude."""
            import shutil
            openclaude_path = shutil.which("openclaude")
            node_path = shutil.which("node")
            
            results = {
                "openclaude_binary": openclaude_path,
                "node_binary": node_path,
                "gateway_online": _gateway_health().get("online", False),
                "mcp_online": _mcp_health().get("online", False),
                "profile_found": OPENCLAUDE_PROFILE.exists()
            }
            
            return {
                "success": all([openclaude_path, node_path, results["gateway_online"]]),
                "action": action,
                "diagnostics": results,
                "timestamp": ts
            }

        elif action == "session.sync":
            """Força sincronização: escreve heartbeat no ledger e verifica conexão."""
            gw = _gateway_health()
            mcp_st = _mcp_health()
            prof = _profile_status()

            # Tenta escrever no ledger do NeoCortex como prova de vida
            from pathlib import Path as _Path
            ledger_path = _Path(__file__).parents[4] / "01_neocortex_framework" / ".neocortex" / "ledger.json"
            sync_entry = {
                "event": "openclaude_sync",
                "timestamp": ts,
                "gateway_online": gw.get("online", False),
                "mcp_online": mcp_st.get("online", False),
                "profile_valid": prof.get("exists", False),
                "agent": "T0",
            }
            ledger_written = False
            if ledger_path.exists():
                try:
                    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
                except Exception:
                    ledger = {"syncs": []}
                if "syncs" not in ledger:
                    ledger["syncs"] = []
                ledger["syncs"].append(sync_entry)
                try:
                    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
                    ledger_written = True
                except Exception:
                    pass

            return {
                "success": gw.get("online", False) and mcp_st.get("online", False),
                "action": action,
                "timestamp": ts,
                "gateway": gw,
                "mcp_server": mcp_st,
                "profile": prof,
                "ledger_synced": ledger_written,
                "sync_record": sync_entry,
            }

        elif action == "session.prompt":
            """Envia um prompt ao OpenClaude (Janela Lateral) via gRPC."""
            if not prompt_text:
                return {"success": False, "action": action, "error": "prompt_text obrigatório"}

            try:
                import grpc
                from .stubs import openclaude_pb2, openclaude_pb2_grpc
                
                # Configuração do Canal
                channel = grpc.insecure_channel('localhost:50051')
                stub = openclaude_pb2_grpc.AgentServiceStub(channel)
                
                # Prepara a mensagem inicial
                request = openclaude_pb2.ChatRequest(
                    message=prompt_text,
                    working_directory=os.getcwd(),
                    session_id=session_id or "default-bridge-session"
                )
                
                client_msg = openclaude_pb2.ClientMessage(request=request)
                
                # Envia via stream
                responses = stub.Chat(iter([client_msg]))
                
                full_text = ""
                tokens = {"prompt": 0, "completion": 0, "total": 0}
                
                for response in responses:
                    if hasattr(response, 'text_chunk'):
                        full_text += response.text_chunk.text
                    elif hasattr(response, 'done'):
                        full_text = response.done.full_text or full_text
                        tokens["prompt"] = response.done.prompt_tokens
                        tokens["completion"] = response.done.completion_tokens
                        tokens["total"] = tokens["prompt"] + tokens["completion"]
                    elif hasattr(response, 'error'):
                        return {"success": False, "action": action, "error": response.error.message}

                return {
                    "success": True,
                    "action": action,
                    "timestamp": ts,
                    "content": full_text,
                    "session_id": session_id,
                    "tokens": tokens,
                    "mode": "grpc-headless (Janela Lateral)"
                }
            except Exception as e:
                logger.error(f"Erro gRPC na Bridge: {e}")
                return {"success": False, "action": action, "error": f"Erro gRPC: {str(e)} (O servidor OpenClaude --headless está rodando?)"}

        elif action == "session.commands":
            """Lista comandos de barra (shash commands) do OpenClaude."""
            try:
                import grpc
                from .stubs import openclaude_pb2, openclaude_pb2_grpc
                channel = grpc.insecure_channel('localhost:50051')
                stub = openclaude_pb2_grpc.AgentServiceStub(channel)
                # Envia um prompt de /help para capturar a lista de comandos via generator
                request = openclaude_pb2.ChatRequest(
                    message="/help",
                    working_directory=os.getcwd(),
                    session_id="help-query"
                )
                client_msg = openclaude_pb2.ClientMessage(request=request)
                responses = stub.Chat(iter([client_msg]))
                full_text = ""
                for response in responses:
                    if hasattr(response, 'text_chunk'):
                        full_text += response.text_chunk.text
                    elif hasattr(response, 'done'):
                        full_text = response.done.full_text or full_text
                
                return {
                    "success": True,
                    "action": action,
                    "timestamp": ts,
                    "commands_raw": full_text
                }
            except Exception as e:
                return {"success": False, "action": action, "error": str(e)}

        else:
            available = [
                "session.status",
                "session.sync",
                "session.prompt",
                "gateway.health",
                "mcp.status",
                "profile.status",
            ]
            return {
                "success": False,
                "error": f"action desconhecida: {action}",
                "available": available,
                "timestamp": ts,
            }
