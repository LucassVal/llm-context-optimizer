from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.796706'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-003-manifest-factory
related_ssot:
  - NC-BOOT-FR-001
  - NC-MAN-FR-001-project-manifest
  - NC-TOOL-FR-019-project-manifest
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-019-project-manifest.py
MCP Tool  Project Manifest Factory

Expe a NC-SCR-FR-003-manifest-factory via MCP.
Permite que qualquer IA conectada ao servidor gere/leia o manifesto completo do projeto.

Actions:
  - generate: Executa scan completo e gera NC-MAN-FR-001-project-manifest.{json,jsonl,md}
  - get_boot_context: Retorna boot_context compacto (enviar para nova IA)
  - get_nc_index: Retorna ndice de todos arquivos NC-* do projeto
  - get_structure: Retorna estrutura de diretrios (filtrada por extenso/padro)
  - get_ssot_files: Retorna apenas os arquivos SSOT crticos
"""

import json
import sys
from datetime import datetime
from pathlib import Path

#  R09: import NC- scripts via importlib
_SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "scripts"  # 01_neocortex_framework/scripts
sys.path.insert(0, str(_SCRIPTS_DIR.parent))  # 01_neocortex_framework/

# Manifest JSON path
_MAN_JSON = (
    Path(__file__).parent.parent.parent.parent
    / "DIR-DOC-FR-001-docs-main"
    / "NC-MAN-FR-001-project-manifest.json"
)


def _load_factory():
    """Import tardio da factory (R09: sem import esttico de arquivo com hfen)."""
    import importlib.util
    factory_path = _SCRIPTS_DIR / "NC-SCR-FR-003-manifest-factory.py"
    spec = importlib.util.spec_from_file_location("nc_manifest_factory", factory_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_cached() -> dict | None:
    """Carrega manifesto JSON em cache (se existir e < 24h)."""
    if not _MAN_JSON.exists():
        return None
    age_h = (datetime.now().timestamp() - _MAN_JSON.stat().st_mtime) / 3600
    if age_h > 24:
        return None
    try:
        return json.loads(_MAN_JSON.read_text(encoding="utf-8"))
    except Exception:
        return None


def register_tool(server):
    """Registra o tool no servidor MCP (FastMCP ou MockMCP)."""

    @server.tool()
    def neocortex_project_manifest(action: str, fmt: str = "all", filter_ext: str = "",
                                   use_cache: bool = True) -> str:
        """Manifest Factory  escaneia TODO o projeto e gera manifesto compacto.

        Actions: generate, get_boot_context, get_nc_index, get_structure, get_ssot_files
        Args: fmt (all|json|md|jsonl), filter_ext, use_cache"""
        action = (action or "").strip().lower()

        if action == "generate":
            try:
                factory = _load_factory()
                manifest = factory.run(fmt=fmt)
                meta = manifest["meta"]
                return json.dumps({
                    "status": "ok",
                    "generated_at": meta["generated_at"],
                    "total_files": meta["total_files"],
                    "total_dirs": meta["total_dirs"],
                    "total_size_mb": meta["total_size_mb"],
                    "nc_named_count": meta["nc_named_count"],
                    "ssot_count": meta["ssot_count"],
                    "output_files": [
                        str(_MAN_JSON),
                        str(_MAN_JSON).replace(".json", ".jsonl"),
                        str(_MAN_JSON).replace(".json", ".md"),
                    ],
                    "tip": "Use 'get_boot_context' para obter o contexto para nova IA.",
                }, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)})

        # Para as demais aes, carrega manifesto (cached ou gera)
        manifest = _load_cached() if use_cache else None
        if manifest is None:
            try:
                factory = _load_factory()
                manifest = factory.run(fmt="json")
            except Exception as e:
                return json.dumps({"status": "error",
                                   "error": f"Manifesto no encontrado e factory falhou: {e}"})

        if action == "get_boot_context":
            return json.dumps({
                "boot_context": manifest.get("boot_context", ""),
                "meta": manifest.get("meta", {}),
                "usage": (
                    "Envie boot_context + contedo de NC-BOOT-FR-001 para qualquer IA via API. "
                    "A IA ter acesso ao ndice completo do projeto sem precisar de acesso aos arquivos."
                ),
            }, ensure_ascii=False, indent=2)

        elif action == "get_nc_index":
            nc_index = manifest.get("nc_index", {})
            return json.dumps({
                "total": len(nc_index),
                "nc_index": nc_index,
            }, ensure_ascii=False, indent=2)

        elif action == "get_ssot_files":
            return json.dumps({
                "total": len(manifest.get("ssot_files", [])),
                "ssot_files": manifest.get("ssot_files", []),
            }, ensure_ascii=False, indent=2)

        elif action == "get_structure":
            structure = manifest.get("structure", {})
            if filter_ext:
                filtered = {}
                for d, entries in structure.items():
                    matching = [e for e in entries if e.get("ext") == filter_ext]
                    if matching:
                        filtered[d] = matching
                structure = filtered
            # Resumo compacto para no sobrecarregar o contexto
            summary = {d: [e["name"] for e in entries] for d, entries in structure.items()}
            return json.dumps({
                "filter_ext": filter_ext or "(all)",
                "dirs": len(summary),
                "structure": summary,
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({
                "error": f"Ao desconhecida: '{action}'",
                "valid_actions": ["generate", "get_boot_context", "get_nc_index",
                                  "get_structure", "get_ssot_files"],
            })
