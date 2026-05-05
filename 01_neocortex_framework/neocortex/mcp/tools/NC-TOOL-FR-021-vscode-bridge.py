"""---
NC-TOOL-FR-021 — neocortex_vscode
VS Code IDE Bridge + DeepSeek Account Tools

WHAT: HTTP JSON-RPC bridge to VS Code extension at localhost:18791 for IDE
      operations (file tree, file read, diagnostics, active editor, git
      status/diff, terminal exec, workspace folders) — plus standalone
      DeepSeek API balance checker (USD/CNY balance + model listing).
WHY: MCP-accessible VS Code IDE control — agents inspect workspace, check
     git status, execute terminal commands without leaving MCP ecosystem.
     DeepSeek balance monitor for cost tracking.
WHERE: Registered as 'neocortex_vscode' — called by agents needing IDE
       introspection, CI/CD workflows, and cost-monitoring routines.

Actions: connect, file_tree, file_read, diagnostics, active_editor,
  git_status, git_diff, terminal_exec, workspace_folders,
  deepseek_balance
---"""



import json
import os
import urllib.error
import urllib.request
from typing import Any

TOOL_NAME = "neocortex_vscode"

BRIDGE_URL = "http://127.0.0.1:18791"

# API key do config.yaml (LiteLLM) — mesma usada no gateway
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or ""


def _bridge_call(tool: str, params: dict | None = None) -> dict:
    """Make a JSON-RPC-style call to the VS Code bridge server."""
    payload = json.dumps({"tool": tool, "params": params or {} }).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {
            "error": f"Cannot connect to VS Code bridge at {BRIDGE_URL}. "
                     f"Make sure the extension is running in VS Code. ({e.reason})"
        }
    except (json.JSONDecodeError, OSError) as e:
        return {"error": str(e)}


def _deepseek_api(path: str, timeout: int = 10) -> Any:
    """Chama a API pública da DeepSeek (sem precisar do gateway)."""
    import ssl
    url = f"https://api.deepseek.com{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


def register_tool(mcp):
    """Register the VS Code bridge tool with the MCP server."""

    @mcp.tool()
    def neocortex_vscode(
        action: str,
        params: str | None = None,
    ) -> str:
        """
        Access VS Code IDE and DeepSeek account tools.

        IDE actions (require VS Code extension running):
          connect           — Health check: is the bridge running?
          file_tree         — List workspace files (params: {"depth": 3})
          file_read         — Read file content (params: {"path": "..."})
          diagnostics       — Get diagnostics for active/target file (params: {"path": "..."})
          active_editor     — Info about the currently open editor
          git_status        — Git status in workspace
          git_diff          — Git diff (params: {"path": "..."} for specific file)
          terminal_exec     — Send command to VS Code terminal (params: {"command": "...", "name": "..."})
          workspace_folders — List workspace folders

        Account actions (no VS Code needed):
          deepseek_balance  — Show DeepSeek account balance and available models

        Args:
          action: The bridge or account action to invoke.
          params: Optional JSON string with parameters for the action.
        """
        parsed_params: dict[str, Any] = {}
        if params:
            try:
                parsed_params = json.loads(params)
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid JSON in params parameter"})

        # ── Account actions (direct DeepSeek API, no bridge needed) ──
        if action == "deepseek_balance":
            try:
                balance = _deepseek_api("/user/balance")
                models = _deepseek_api("/models")
                available = [
                    m["id"] for m in models.get("data", [])
                    if "deepseek" in m["id"]
                ]
                infos = balance.get("balance_infos", [])
                usd = next((b for b in infos if b["currency"] == "USD"), {})
                cny = next((b for b in infos if b["currency"] == "CNY"), {})
                return json.dumps({
                    "account_available": balance.get("is_available", False),
                    "balance_usd": float(usd.get("total_balance", 0)),
                    "balance_cny": float(cny.get("total_balance", 0)),
                    "granted_usd": float(usd.get("granted_balance", 0)),
                    "topped_up_usd": float(usd.get("topped_up_balance", 0)),
                    "available_models": available,
                    "note": "deepseek-v4-pro usado como padrão no gateway local (:4001). deepseek-v4-flash disponível como alternativa."
                }, indent=2, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"error": f"DeepSeek API error: {e}"})

        # ── IDE actions (require bridge) ──
        result = _bridge_call(action, parsed_params)

        if "error" in result:
            return json.dumps({"error": result["error"]})

        if "result" in result:
            return json.dumps(result["result"], indent=2, ensure_ascii=False)

        return json.dumps(result, indent=2, ensure_ascii=False)
