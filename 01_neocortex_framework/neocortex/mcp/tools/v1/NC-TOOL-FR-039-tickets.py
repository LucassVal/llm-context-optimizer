from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-18T09:35:00.000000'
  injected_by: T0-Antigravity
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-039-tickets
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
  - governance
---"""
"""
NC-TOOL-FR-039-tickets.py
FR-039  MCP Tool: neocortex_tickets

Gerencia tickets e roadmap do NeoCortex (G-002, G-003, G-008, G-013).

Ações:
  ticket.create       cria YAML de ticket em DIR-DS-001-tickets/
  ticket.list         lista tickets com status e idade
  ticket.close        fecha ticket (status DONE)
  ticket.archive      move tickets >N dias para DIR-DS-004-archived-tickets/
  ticket.orphan       tickets sem handoff correspondente (G-003)
  roadmap.mark_done   marca %DONE no NC-TODO-FR-001 (roadmap .md) (G-013)
  roadmap.read        lê seções do rodamap
"""

import logging
import re
import shutil
from datetime import datetime, timedelta, timezone
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


def _tickets_dir(root: Path) -> Path:
    return root / "DIR-DS-001-tickets"


def _audit_dir(root: Path) -> Path:
    return root / "DIR-DS-002-audit-logs"


def _archive_tickets_dir(root: Path) -> Path:
    return root / "DIR-DS-004-archived-tickets"


def _roadmap_path(root: Path) -> Path:
    return root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-TODO-FR-001-project-roadmap-consolidated.md"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def _ticket_create(
    ticket_id: str,
    title: str,
    description: str,
    priority: str = "MEDIUM",
    assigned_to: str = "T0-Antigravity",
    tags: list = None,
) -> Dict[str, Any]:
    root = _get_project_root()
    tdir = _tickets_dir(root)
    tdir.mkdir(parents=True, exist_ok=True)

    ts_iso = datetime.now(timezone.utc).isoformat()
    fname = f"{ticket_id}-ticket.yaml"
    path = tdir / fname

    tag_list = tags or []
    content = f"""ticket_id: "{ticket_id}"
title: "{title}"
status: "OPEN"
priority: "{priority}"
created_at: "{ts_iso}"
assigned_to: "{assigned_to}"
tags: {tag_list}
description: |
  {description.strip()}
acceptance_criteria: []
files_affected: []
notes: ""
"""
    try:
        path.write_text(content, encoding="utf-8")
        return {"success": True, "file": fname, "path": str(path), "ticket_id": ticket_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _ticket_list(status_filter: str = "", limit: int = 30) -> Dict[str, Any]:
    root = _get_project_root()
    tdir = _tickets_dir(root)
    if not tdir.exists():
        return {"success": True, "tickets": [], "count": 0}

    tickets = []
    for f in sorted(tdir.glob("*.yaml"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        if "TEMPLATE" in f.name:
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        status_match = re.search(r'status:\s*"?([^"\n]+)', content)
        id_match = re.search(r'ticket_id:\s*"?([^"\n]+)', content)
        title_match = re.search(r'title:\s*"?([^"\n]+)', content)
        status = status_match.group(1).strip('"') if status_match else "UNKNOWN"
        if status_filter and status.upper() != status_filter.upper():
            continue
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        tickets.append({
            "file": f.name,
            "ticket_id": id_match.group(1).strip('"') if id_match else f.stem,
            "title": title_match.group(1).strip('"') if title_match else "",
            "status": status,
            "age_days": age_days,
        })
    return {"success": True, "tickets": tickets, "count": len(tickets)}


def _ticket_close(ticket_id: str) -> Dict[str, Any]:
    root = _get_project_root()
    tdir = _tickets_dir(root)
    matches = list(tdir.glob(f"{ticket_id}*.yaml"))
    if not matches:
        return {"success": False, "error": f"Ticket {ticket_id} não encontrado"}
    path = matches[0]
    content = path.read_text(encoding="utf-8")
    if 'status: "DONE"' in content or "status: DONE" in content:
        return {"success": True, "message": f"{ticket_id} já está DONE", "file": path.name}
    content = re.sub(r'status:\s*"?[^"\n]+"?', 'status: "DONE"', content, count=1)
    ts = datetime.now(timezone.utc).isoformat()
    content += f'\nclosed_at: "{ts}"\n'
    path.write_text(content, encoding="utf-8")
    return {"success": True, "ticket_id": ticket_id, "file": path.name, "status": "DONE"}


def _ticket_archive(older_than_days: int = 30) -> Dict[str, Any]:
    root = _get_project_root()
    tdir = _tickets_dir(root)
    arc = _archive_tickets_dir(root)
    arc.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=older_than_days)
    moved = []
    for f in tdir.glob("*.yaml"):
        if "TEMPLATE" in f.name:
            continue
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            dest = arc / f.name
            shutil.move(str(f), str(dest))
            moved.append(f.name)
    return {"success": True, "moved": moved, "count": len(moved), "older_than_days": older_than_days}


def _ticket_orphan() -> Dict[str, Any]:
    """Tickets sem handoff correspondente (G-003)."""
    root = _get_project_root()
    tdir = _tickets_dir(root)
    adir = _audit_dir(root)

    ticket_ids = set()
    for f in tdir.glob("*.yaml"):
        m = re.search(r"(NC-DS-\d+)", f.name)
        if m:
            ticket_ids.add(m.group(1))

    handoff_ids = set()
    for f in adir.glob("*.yaml"):
        m = re.search(r"(NC-DS-\d+)", f.name)
        if m:
            handoff_ids.add(m.group(1))

    orphan_t = sorted(ticket_ids - handoff_ids)
    orphan_h = sorted(handoff_ids - ticket_ids)
    ok = len(orphan_t) == 0

    return {
        "success": ok,
        "tickets_total": len(ticket_ids),
        "handoffs_total": len(handoff_ids),
        "orphan_tickets_no_handoff": orphan_t,
        "orphan_handoffs_no_ticket": orphan_h,
        "status": "OK" if ok else f"BLOQUEANTE: {len(orphan_t)} tickets sem handoff",
    }


def _roadmap_mark_done(ticket_id: str) -> Dict[str, Any]:
    """Marca ticket como %DONE no NC-TODO-FR-001 (G-013)."""
    root = _get_project_root()
    rmap = _roadmap_path(root)
    if not rmap.exists():
        return {"success": False, "error": f"Roadmap não encontrado: {rmap}"}

    content = rmap.read_text(encoding="utf-8")
    # Procura linha com o ticket_id e troca [ ] ou [/] por [x]
    pattern = re.compile(rf"(\s*[-*]\s*)\[[ /]\](\s.*{re.escape(ticket_id)}.*)")
    new_content, n = pattern.subn(r"\1[x]\2", content)

    if n == 0:
        # Tenta adicionar comentário %DONE junto ao ticket_id na linha
        pattern2 = re.compile(rf"(.*{re.escape(ticket_id)}.*)")
        def replacer(m):
            line = m.group(1)
            if "%DONE" not in line:
                return line + "  <!-- %DONE -->"
            return line
        new_content2, n2 = pattern2.subn(replacer, content)
        if n2:
            rmap.write_text(new_content2, encoding="utf-8")
            return {"success": True, "ticket_id": ticket_id, "action": "comment_added", "matches": n2}
        return {"success": False, "error": f"{ticket_id} não encontrado no roadmap"}

    rmap.write_text(new_content, encoding="utf-8")
    return {"success": True, "ticket_id": ticket_id, "action": "marked_done", "lines_updated": n}


def _roadmap_read(section: str = "") -> Dict[str, Any]:
    root = _get_project_root()
    rmap = _roadmap_path(root)
    if not rmap.exists():
        return {"success": False, "error": f"Roadmap não encontrado: {rmap}"}
    content = rmap.read_text(encoding="utf-8")
    if section:
        # Extrai a seção pelo heading
        m = re.search(rf"(#{1,3} .*{re.escape(section)}.*\n(?:.*\n)*?)(?=#{1,3} |\Z)", content, re.IGNORECASE)
        if m:
            return {"success": True, "section": section, "content": m.group(1)[:3000]}
        return {"success": False, "error": f"Seção '{section}' não encontrada"}
    return {"success": True, "content": content[:4000], "total_chars": len(content)}


# ---------------------------------------------------------------------------
# Register MCP tool
# ---------------------------------------------------------------------------

def register_tool(mcp) -> None:
    """Registra neocortex_tickets no servidor MCP."""

    @mcp.tool(name="neocortex_tickets")
    def neocortex_tickets(
        action: str,
        ticket_id: str = "",
        title: str = "",
        description: str = "",
        priority: str = "MEDIUM",
        assigned_to: str = "T0-Antigravity",
        tags: str = "[]",
        status_filter: str = "",
        limit: int = 30,
        older_than_days: int = 30,
        section: str = "",
    ) -> Dict[str, Any]:
        """Gerencia tickets e roadmap do NeoCortex (NC-WF-001 CICLO 1/2/4).

        Aes: ticket.create, ticket.list, ticket.close, ticket.archive, ticket.orphan,
             roadmap.mark_done, roadmap.read"""
        import json

        if action == "ticket.create":
            if not ticket_id or not title:
                return {"success": False, "error": "ticket_id e title são obrigatórios"}
            try:
                tag_list = json.loads(tags) if tags else []
            except Exception:
                tag_list = []
            return _ticket_create(ticket_id, title, description, priority, assigned_to, tag_list)

        elif action == "ticket.list":
            return _ticket_list(status_filter=status_filter, limit=limit)

        elif action == "ticket.close":
            if not ticket_id:
                return {"success": False, "error": "ticket_id obrigatório para ticket.close"}
            return _ticket_close(ticket_id)

        elif action == "ticket.archive":
            return _ticket_archive(older_than_days=older_than_days)

        elif action == "ticket.orphan":
            return _ticket_orphan()

        elif action == "roadmap.mark_done":
            if not ticket_id:
                return {"success": False, "error": "ticket_id obrigatório para roadmap.mark_done"}
            return _roadmap_mark_done(ticket_id)

        elif action == "roadmap.read":
            return _roadmap_read(section=section)

        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'",
                "available": [
                    "ticket.create", "ticket.list", "ticket.close",
                    "ticket.archive", "ticket.orphan",
                    "roadmap.mark_done", "roadmap.read",
                ],
            }
