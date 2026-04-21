from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-18T09:35:00.000000'
  injected_by: T0-Antigravity
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-040-governance-ops
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
  - governance
---"""
"""
NC-TOOL-FR-040-governance-ops.py
FR-040  MCP Tool: neocortex_governance_ops

Operações de manutenção de governança NeoCortex (G-004, G-005, G-007).

Ações:
  bootup.sync        sincroniza bootup com handoffs recentes (NC-SCR-FR-066)
  bootup.read        lê seção do boot manifest
  catalog.check_age  verifica idade do artifact_catalog.json (G-007)
  catalog.refresh    regenera artifact_catalog.json via NC-SCR-FR-064
  yaml.sanitize      valida/sanitiza YAMLs de governança (NC-SCR-FR-009)
  naming.audit       verifica conformidade de nomes NC- no filesystem (G-009)
  handoff.archive    move handoffs >N dias para DIR-ARC-FR-001 (G-008)
"""

import logging
import subprocess
import sys
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


def _run_script(script_path: Path, args: list = None, cwd: Path = None) -> Dict[str, Any]:
    if not script_path.exists():
        return {"success": False, "error": f"Script não encontrado: {script_path}"}
    cmd = [sys.executable, str(script_path)] + (args or [])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or script_path.parent), timeout=60)
    return {
        "success": r.returncode == 0,
        "returncode": r.returncode,
        "stdout": r.stdout.strip()[:2000] if r.stdout else "",
        "stderr": r.stderr.strip()[:1000] if r.stderr else "",
    }


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def _bootup_sync(root: Path) -> Dict[str, Any]:
    script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-066-bootup-sync.py"
    return _run_script(script, cwd=root)


def _bootup_read(root: Path, section: str = "") -> Dict[str, Any]:
    import re
    boot_path = root / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md"
    if not boot_path.exists():
        return {"success": False, "error": f"Boot manifest não encontrado: {boot_path}"}
    content = boot_path.read_text(encoding="utf-8")
    if section:
        m = re.search(rf"(#{1,3}[^\n]*{re.escape(section)}[^\n]*\n(?:.*\n)*?)(?=#{1,3} |\Z)", content, re.IGNORECASE)
        if m:
            return {"success": True, "section": section, "content": m.group(1)[:3000]}
        return {"success": False, "error": f"Seção '{section}' não encontrada"}
    # Retorna primeiras 100 linhas (boot summary)
    lines = content.splitlines()[:100]
    return {"success": True, "content": "\n".join(lines), "total_lines": len(content.splitlines())}


def _catalog_check_age(root: Path) -> Dict[str, Any]:
    import json
    catalog_path = root / "DIR-DOC-FR-001-docs-main" / "artifact_catalog.json"
    if not catalog_path.exists():
        return {"success": False, "error": "artifact_catalog.json não encontrado", "needs_refresh": True}
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        gen_str = data.get("metadata", {}).get("generated", "")
        if gen_str:
            gen = datetime.fromisoformat(gen_str.replace("Z", "+00:00"))
            age_h = (datetime.now(timezone.utc) - gen).total_seconds() / 3600
        else:
            age_h = 9999.0
        py_count = len(data.get("python_files", []))
        yaml_count = len(data.get("yaml_files", []))
        needs_refresh = age_h > 24
        return {
            "success": True,
            "age_hours": round(age_h, 1),
            "needs_refresh": needs_refresh,
            "python_files": py_count,
            "yaml_files": yaml_count,
            "status": "WARN: >24h — regenerar" if needs_refresh else "OK",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "needs_refresh": True}


def _catalog_refresh(root: Path) -> Dict[str, Any]:
    script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-064-artifact-catalog.py"
    return _run_script(script, cwd=root)


def _yaml_sanitize(root: Path, check_only: bool = True) -> Dict[str, Any]:
    script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-009-sanitize-all-yamls.py"
    args = ["--check-only"] if check_only else []
    return _run_script(script, args=args, cwd=root)


def _naming_audit(root: Path, max_results: int = 20) -> Dict[str, Any]:
    import re as _re
    pattern = _re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}-.+\..+$")
    skip_dirs = {".git", "__pycache__", ".venv", "node_modules", ".agents"}
    non_conform = []
    total = 0
    for path in root.rglob("*"):
        if path.is_file() and not any(s in path.parts for s in skip_dirs):
            if path.suffix in (".py", ".md", ".yaml", ".json", ".mdc"):
                total += 1
                if not pattern.match(path.name):
                    non_conform.append(str(path.relative_to(root)))
    sample = non_conform[:max_results]
    pct_ok = round((total - len(non_conform)) / total * 100, 1) if total else 100.0
    return {
        "success": len(non_conform) == 0,
        "total_files": total,
        "non_conformant": len(non_conform),
        "compliance_pct": pct_ok,
        "sample": sample,
        "status": "OK" if len(non_conform) == 0 else f"WARN: {len(non_conform)} arquivos fora do padrão NC-",
    }


def _handoff_archive(root: Path, older_than_days: int = 7) -> Dict[str, Any]:
    import shutil
    audit = root / "DIR-DS-002-audit-logs"
    archive = root / "DIR-ARC-FR-001-archive-main"
    archive.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=older_than_days)
    moved = []
    for f in audit.glob("*.yaml"):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            dest = archive / f.name
            shutil.move(str(f), str(dest))
            moved.append(f.name)
    return {"success": True, "moved": moved, "count": len(moved), "older_than_days": older_than_days}


# ---------------------------------------------------------------------------
# Register MCP tool
# ---------------------------------------------------------------------------

def register_tool(mcp) -> None:
    """Registra neocortex_governance_ops no servidor MCP."""

    @mcp.tool(name="neocortex_governance_ops")
    def neocortex_governance_ops(
        action: str,
        section: str = "",
        check_only: bool = True,
        older_than_days: int = 7,
        max_results: int = 20,
    ) -> Dict[str, Any]:
        """Operaes de manuteno de governana NeoCortex (NC-WF-001 CICLO 3/4).

        Aes: bootup.sync, bootup.read, catalog.check_age, catalog.refresh,
             yaml.sanitize, naming.audit, handoff.archive

        Args:
            action:          Ao desejada
            section:         Seo para bootup.read (ex: '9', 'tickets crticos')
            check_only:      Se True, yaml.sanitize apenas verifica (no modifica)
            older_than_days: Limiar de idade para handoff.archive
            max_results:     Mximo de resultados em naming.audit"""
        root = _get_project_root()

        if action == "bootup.sync":
            return _bootup_sync(root)

        elif action == "bootup.read":
            return _bootup_read(root, section=section)

        elif action == "catalog.check_age":
            return _catalog_check_age(root)

        elif action == "catalog.refresh":
            return _catalog_refresh(root)

        elif action == "yaml.sanitize":
            return _yaml_sanitize(root, check_only=check_only)

        elif action == "naming.audit":
            return _naming_audit(root, max_results=max_results)

        elif action == "handoff.archive":
            return _handoff_archive(root, older_than_days=older_than_days)

        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'",
                "available": [
                    "bootup.sync", "bootup.read",
                    "catalog.check_age", "catalog.refresh",
                    "yaml.sanitize", "naming.audit", "handoff.archive",
                ],
            }
