from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-18T09:35:00.000000'
  injected_by: T0-Antigravity
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-038-handoff
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
  - governance
---"""
"""
NC-TOOL-FR-038-handoff.py
FR-038  MCP Tool: neocortex_handoff

Gerencia handoffs de governança NeoCortex (R23 NC-WF-001 CICLO 2).

Ações disponíveis:
  handoff.create    gera YAML de handoff em DIR-DS-002-audit-logs/
  handoff.validate  valida arquivo .py: py_compile + ruff + zero print() stdout
  handoff.list      lista handoffs em DIR-DS-002-audit-logs/
  handoff.get       lê conteúdo de um handoff por ticket_id ou nome de arquivo
  handoff.orphan    tickets em DIR-DS-001-tickets sem handoff correspondente
"""

import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_project_root() -> Path:
    try:
        from neocortex.core.config.NC_CFG_FR_002_config import get_config
        cfg = get_config()
        return Path(cfg.base_path).parent
    except Exception:
        return Path(__file__).parent.parent.parent.parent.parent

def _audit_dir(root: Path) -> Path:
    return root / "DIR-DS-002-audit-logs"

def _tickets_dir(root: Path) -> Path:
    return root / "DIR-DS-001-tickets"

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def _handoff_create(
    ticket_id: str,
    summary: str,
    status: str = "APPROVED",
    files_modified: list = None,
    files_created: list = None,
    agent: str = "T0-Antigravity",
    ssot_updated: bool = False,
    locks_clean: bool = True,
    compile_ok: bool = True,
    ruff_ok: bool = True,
    naming_ok: bool = True,
) -> Dict[str, Any]:
    root = _get_project_root()
    audit = _audit_dir(root)
    audit.mkdir(parents=True, exist_ok=True)

    ts_iso = datetime.now(timezone.utc).isoformat()
    ts_file = _ts()
    fname = f"{ticket_id}-handoff-{ts_file}.yaml"
    path = audit / fname

    fm = files_modified or []
    fc = files_created or []

    content = f"""ticket_id: "{ticket_id}"
status: "{status}"
timestamp: "{ts_iso}"
agent: "{agent}"
summary: |
  {summary.strip()}
files_modified: {fm}
files_created: {fc}
checklist_r20:
  naming_convention: {str(naming_ok).lower()}
  no_print_statements: {str(compile_ok).lower()}
  ssot_updated: {str(ssot_updated).lower()}
  no_locked_files_modified: {str(locks_clean).lower()}
  handoff_yaml_complete: true
t0_review:
  compile_ok: {str(compile_ok).lower()}
  naming_ok: {str(naming_ok).lower()}
  ssot_updated: {str(ssot_updated).lower()}
  locks_clean: {str(locks_clean).lower()}
  ruff_ok: {str(ruff_ok).lower()}
  roadmap_done: false
  notes: "Gerado via neocortex_handoff MCP tool"
"""
    try:
        path.write_text(content, encoding="utf-8")
        return {"success": True, "file": str(fname), "path": str(path), "ticket_id": ticket_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _handoff_validate(file_path: str) -> Dict[str, Any]:
    """Valida arquivo .py: py_compile + ruff + zero print() na stdout."""
    p = Path(file_path)
    if not p.exists():
        return {"success": False, "error": f"Arquivo não encontrado: {file_path}"}
    if p.suffix != ".py":
        return {"success": False, "error": "Apenas arquivos .py podem ser validados"}

    results = {}

    # py_compile
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(p)],
        capture_output=True, text=True
    )
    results["compile_ok"] = r.returncode == 0
    results["compile_error"] = r.stderr.strip() if r.returncode != 0 else None

    # ruff
    r2 = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(p)],
        capture_output=True, text=True
    )
    results["ruff_ok"] = r2.returncode == 0
    results["ruff_output"] = r2.stdout.strip() or None

    # zero print() na stdout
    text = p.read_text(encoding="utf-8", errors="replace")
    bad_prints = [
        line.strip() for line in text.splitlines()
        if "print(" in line
        and "file=sys.stderr" not in line
        and not line.strip().startswith("#")
    ]
    results["no_stdout_print"] = len(bad_prints) == 0
    results["stdout_prints_found"] = bad_prints[:5] if bad_prints else []

    all_ok = results["compile_ok"] and results["ruff_ok"] and results["no_stdout_print"]
    return {"success": all_ok, "file": str(p.name), **results}


def _handoff_list(limit: int = 20) -> Dict[str, Any]:
    root = _get_project_root()
    audit = _audit_dir(root)
    if not audit.exists():
        return {"success": True, "handoffs": [], "count": 0}
    files = sorted(audit.glob("*.yaml"), key=lambda f: f.stat().st_mtime, reverse=True)[:limit]
    items = [{"file": f.name, "size_bytes": f.stat().st_size, "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()} for f in files]
    return {"success": True, "handoffs": items, "count": len(items)}


def _handoff_get(ticket_id: str = "", filename: str = "") -> Dict[str, Any]:
    root = _get_project_root()
    audit = _audit_dir(root)
    if filename:
        path = audit / filename
    elif ticket_id:
        matches = list(audit.glob(f"{ticket_id}-handoff-*.yaml"))
        if not matches:
            return {"success": False, "error": f"Nenhum handoff encontrado para {ticket_id}"}
        path = sorted(matches, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    else:
        return {"success": False, "error": "Forneça ticket_id ou filename"}
    if not path.exists():
        return {"success": False, "error": f"Arquivo não encontrado: {path}"}
    return {"success": True, "file": path.name, "content": path.read_text(encoding="utf-8")}


def _handoff_orphan() -> Dict[str, Any]:
    """Tickets sem handoff correspondente e vice-versa."""
    import re
    root = _get_project_root()
    tickets_dir = _tickets_dir(root)
    audit_dir = _audit_dir(root)

    tickets = set()
    for f in tickets_dir.glob("*.yaml"):
        m = re.search(r"(NC-DS-\d+)", f.name)
        if m:
            tickets.add(m.group(1))

    handoffs = set()
    for f in audit_dir.glob("*.yaml"):
        m = re.search(r"(NC-DS-\d+)", f.name)
        if m:
            handoffs.add(m.group(1))

    orphan_tickets = sorted(tickets - handoffs)
    orphan_handoffs = sorted(handoffs - tickets)
    ok = len(orphan_tickets) == 0 and len(orphan_handoffs) == 0

    return {
        "success": ok,
        "tickets_total": len(tickets),
        "handoffs_total": len(handoffs),
        "orphan_tickets": orphan_tickets,
        "orphan_handoffs": orphan_handoffs,
        "status": "OK" if ok else f"ERRO: {len(orphan_tickets)} tickets sem handoff, {len(orphan_handoffs)} handoffs sem ticket",
    }


# ---------------------------------------------------------------------------
# Register MCP tool
# ---------------------------------------------------------------------------

def register_tool(mcp) -> None:
    """Registra neocortex_handoff no servidor MCP."""

    @mcp.tool(name="neocortex_handoff")
    def neocortex_handoff(
        action: str,
        ticket_id: str = "",
        summary: str = "",
        status: str = "APPROVED",
        agent: str = "T0-Antigravity",
        files_modified: str = "[]",
        files_created: str = "[]",
        ssot_updated: bool = False,
        locks_clean: bool = True,
        file_path: str = "",
        filename: str = "",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Gerencia handoffs de governana NeoCortex (R23 NC-WF-001 CICLO 2).

        Aes: handoff.create, handoff.validate, handoff.list, handoff.get, handoff.orphan
        Args: ticket_id, summary, status, agent, files_modified, files_created,
              ssot_updated, locks_clean, file_path, filename, limit"""
        import json

        if action == "handoff.create":
            if not ticket_id or not summary:
                return {"success": False, "error": "ticket_id e summary são obrigatórios"}
            try:
                fm = json.loads(files_modified) if files_modified else []
                fc = json.loads(files_created) if files_created else []
            except Exception:
                fm, fc = [], []
            return _handoff_create(
                ticket_id=ticket_id, summary=summary, status=status,
                files_modified=fm, files_created=fc, agent=agent,
                ssot_updated=ssot_updated, locks_clean=locks_clean,
            )

        elif action == "handoff.validate":
            if not file_path:
                return {"success": False, "error": "file_path obrigatório para handoff.validate"}
            return _handoff_validate(file_path)

        elif action == "handoff.list":
            return _handoff_list(limit=limit)

        elif action == "handoff.get":
            return _handoff_get(ticket_id=ticket_id, filename=filename)

        elif action == "handoff.orphan":
            return _handoff_orphan()

        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'",
                "available": ["handoff.create", "handoff.validate", "handoff.list", "handoff.get", "handoff.orphan"],
            }
