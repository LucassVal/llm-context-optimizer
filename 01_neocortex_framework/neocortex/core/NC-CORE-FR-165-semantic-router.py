"""---
@Router NC-CORE-FR-165-semantic-router mcp NC-CORE-FR-165-semantic-router.py — Semantic Route
---
"""

import json
import os
import pathlib
import re
from typing import Any


class SemanticRouter:
    """Roteador universal — coracao do NeoCortex."""

    # Aliases: NC-ID antigo → NC-ID novo (24 refs quebradas corrigidas)
    NC_ALIASES = {
        "NC-SVC-FR-001-save-point-service": "NC-CORE-FR-022-save-point-service",
        "NC-SVC-FR-003-savepoint-stub": "NC-CORE-FR-022-save-point-service",
        "NC-SVC-FR-016-wal-service": "NC-CORE-FR-123-regression-service",
        "NC-SVC-FR-017-crypto-hub": "NC-CORE-FR-159-crypto-integrity",
        "NC-CORE-FR-020-circuit-breaker": "NC-CORE-FR-107-circuit-breaker",
        "NC-CORE-FR-021-agent-policy-enforcer": "NC-CORE-FR-101-agent-policy-enforcer",
        "NC-CORE-FR-022-cascade-consolidator": "NC-CORE-FR-105-cascade-consolidator",
        "NC-CORE-FR-023-lexico-service": "NC-CORE-FR-116-lexico-service",
        # Old service patterns -> new core modules
        "NC-SVC-FR-002-metrics-collector": "NC-CORE-FR-154-corporate-engines",
        "NC-SVC-FR-004-session-memory-writer": "NC-CORE-FR-128-session-memory-writer",
        "NC-SVC-FR-005-tool-guard": "NC-CORE-FR-125-tool-guard",
        "NC-SVC-FR-006-search-service": "NC-CORE-FR-126-search-service",
        "NC-SVC-FR-007-knowledge-service": "NC-CORE-FR-127-knowledge-service",
        "NC-SVC-FR-008-regression-service": "NC-CORE-FR-123-regression-service",
        "NC-SVC-FR-009-security-service": "NC-CORE-FR-124-security-service",
        "NC-SVC-FR-010-checkpoint-service": "NC-CORE-FR-106-checkpoint-service",
        "NC-SVC-FR-011-cortex-service": "NC-CORE-FR-110-cortex-service",
        "NC-SVC-FR-012-export-service": "NC-CORE-FR-111-export-service",
        "NC-SVC-FR-013-init-service": "NC-CORE-FR-113-init-service",
        "NC-SVC-FR-014-lobe-service": "NC-CORE-FR-117-lobe-service",
        "NC-SVC-FR-015-manifest-service": "NC-CORE-FR-118-manifest-service",
        "NC-SVC-FR-018-profile-manager": "NC-CORE-FR-120-profile-manager",
        "NC-SVC-FR-019-config-service": "NC-CORE-FR-108-config-service",
        "NC-SVC-FR-020-benchmark-service": "NC-CORE-FR-104-benchmark-service",
    }

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(
            os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3])
        )
        self._cache = None
        self._cache_ts = 0
        self._overrides: dict[str, str] = {}

    def resolve_alias(self, nc_id: str) -> str:
        """Resolve alias: NC-ID antigo → NC-ID novo."""
        return self.NC_ALIASES.get(nc_id, nc_id)

    def _load_catalog(self) -> dict:
        import time

        if self._cache and time.time() - self._cache_ts < 60:
            return self._cache
        cat_file = (
            self.root
            / "01_neocortex_framework"
            / ".neocortex"
            / "lexico"
            / "NC-LEXICO-LATEST.json"
        )
        if cat_file.exists():
            self._cache = json.loads(cat_file.read_text(encoding="utf-8"))
        else:
            self._cache = {}
        self._cache_ts = time.time()
        return self._cache

    def resolve(self, query: str) -> dict:
        """Resolve query para path e modulo. Ex: 'FR-154', 'KPI', 'governance'"""
        result = {"query": query, "found": False, "matches": []}
        catalog = self._load_catalog()

        # 1. Buscar por NC-ID exato (FR-154, FR-129, etc.)
        if re.match(r"FR-\d+", query, re.IGNORECASE):
            ncid = f"NC-CORE-{query}" if not query.startswith("NC-") else query
            result["matches"].append(
                {
                    "type": "engine",
                    "id": ncid,
                    "path": f"01_neocortex_framework/neocortex/core/{ncid}.py",
                    "load": "importlib",
                }
            )

        # 2. Buscar por nome de tool
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        for t in sorted(tools_dir.glob("NC-SUPER-*.py")):
            if query.lower().replace(" ", "") in t.stem.lower().replace("-", ""):
                result["matches"].append(
                    {
                        "type": "tool",
                        "id": t.stem,
                        "path": str(t.relative_to(self.root)),
                        "load": "mcp",
                    }
                )

        # 3. Buscar por dominio (governance, security, etc.)
        domains = catalog.get("domains", {})
        for dom, data in domains.items():
            if query.lower() in dom.lower():
                result["matches"].append(
                    {
                        "type": "domain",
                        "id": dom,
                        "lobes": data.get("count", 0),
                        "path": f"02_memory_lobes/{dom}/",
                    }
                )

        # 4. Buscar por conceito no ULQ
        ulq_file = (
            self.root
            / "01_neocortex_framework"
            / "DIR-DOC-FR-001-docs-main"
            / "NC-DOC-FR-001-ubiquitous-language-dictionary.md"
        )
        if ulq_file.exists():
            ulq = ulq_file.read_text("utf-8", errors="ignore")
            for line in ulq.split("\n"):
                if query.lower() in line.lower() and "|" in line:
                    result["matches"].append(
                        {
                            "type": "ulq_term",
                            "id": query,
                            "definition": line.strip()[:100],
                        }
                    )

        result["found"] = len(result["matches"]) > 0
        result["route"] = result["matches"][0] if result["matches"] else None
        return result

    # ─── ULQ SYMBOL RESOLVER (@/$/%/#) ──────────────────────────

    def _load_ulq_dictionary(self) -> dict:
        """Carrega e parseia o dicionario ULQ markdown em tabelas de simbolos."""
        ulq_file = (
            self.root
            / "01_neocortex_framework"
            / "DIR-DOC-FR-001-docs-main"
            / "NC-DOC-FR-001-ubiquitous-language-dictionary.md"
        )
        if not ulq_file.exists():
            return {"@": {}, "$": {}, "%": {}, "#": {}}

        content = ulq_file.read_text("utf-8", errors="ignore")
        symbols = {"@": {}, "$": {}, "%": {}, "#": {}}
        current_section = None

        for line in content.split("\n"):
            line = line.strip()
            if "Símbolos @" in line or "Referência de Arquivos SSOT" in line:
                current_section = "@"
                continue
            if "Regiões Cerebrais" in line or "Agentes-Lobes" in line:
                current_section = "$"
                continue
            if "Tickets e Ações" in line:
                current_section = "%"
                continue
            if "Serviços e Componentes" in line or "Super-Tools MCP" in line:
                current_section = "#"
                continue
            if line.startswith("##") or line.startswith("---"):
                current_section = None
                continue

            if current_section and "|" in line and "`@" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    symbol = parts[1].replace("`", "").strip()
                    path = parts[3].replace("`", "").strip()
                    desc = parts[2].strip() if len(parts) > 2 else ""
                    symbols[current_section][symbol] = {"path": path, "desc": desc}

            elif (
                current_section
                and "|" in line
                and ("`$" in line or "`%" in line or "`#" in line)
            ):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    symbol = parts[1].replace("`", "").strip()
                    path_or_desc = parts[3].replace("`", "").strip()
                    desc = parts[2].strip() if len(parts) > 2 else ""
                    symbols[current_section][symbol] = {
                        "path": path_or_desc,
                        "desc": desc,
                    }

        return symbols

    def resolve_symbol(self, symbol: str) -> dict:
        """Resolve simbolo ULQ (@/$/%/#) para path real, com decay chain.

        Exemplos:
          resolve_symbol('@LOCKS') → {path: '01_neocortex/.../NC-SEC-FR-001.yaml', found: true}
          resolve_symbol('$FRONTAL') → {region: 'FRONTAL', function: 'Planejamento', found: true}
          resolve_symbol('#GOV') → {tool: 'neocortex_governance', found: true}
          resolve_symbol('%NOW') → {ticket: '...', status: '🔴', found: true}
        """
        result = {"symbol": symbol, "found": False, "type": None}

        # Identify symbol type
        if symbol.startswith("@"):
            result["type"] = "ssot_file"
        elif symbol.startswith("$"):
            result["type"] = "brain_region"
        elif symbol.startswith("%"):
            result["type"] = "ticket_action"
        elif symbol.startswith("#"):
            result["type"] = "service_tool"
        else:
            result["error"] = "Unknown symbol prefix. Use @, $, % or #."
            return result

        # Level 1: ULQ dictionary lookup
        ulq = self._load_ulq_dictionary()
        section = ulq.get(symbol[0], {})  # @, $, %, #

        if symbol in section:
            entry = section[symbol]
            result.update(entry)
            result["found"] = True
            result["level"] = "ULQ"
            if result["type"] == "ssot_file":
                result["full_path"] = (
                    str(self.root / entry["path"]) if entry.get("path") else None
                )
            return result

        # Level 2: TAG INDEX fallback
        tag_file = (
            self.root
            / "01_neocortex_framework"
            / ".neocortex"
            / "lexico"
            / "NC-ULQ-TAG-INDEX.json"
        )
        if tag_file.exists():
            try:
                tag_index = json.loads(tag_file.read_text(encoding="utf-8"))
                symbol_idx = tag_index.get("symbol_index", {})
                for prefix, syms in symbol_idx.items():
                    if symbol in syms:
                        result["found"] = True
                        result["level"] = "TAG_INDEX"
                        result["note"] = f"Found in tag index, prefix={prefix}"
                        return result
            except Exception:
                pass

        # Level 3: PREP regex fallback — search codebase for symbol reference
        result["level"] = "PREP_FALLBACK"
        result["decay"] = "Symbol not found in ULQ or TAG_INDEX. Consider registering."
        return result

    # ─── SANDBOX OVERRIDE ──────────────────────────────────────

    def override(self, symbol: str, temp_path: str) -> dict:
        """Restaura o path original de um simbolo ULQ."""
        if symbol in self._overrides:
            del self._overrides[symbol]
            return {"symbol": symbol, "status": "restored"}
        return {"symbol": symbol, "status": "not_overridden"}

    def resolve_path(self, symbol: str) -> pathlib.Path | None:
        """Conveniencia: resolve simbolo @ e retorna Path absoluto ou None.
        Respeita overrides de sandbox."""
        if symbol in self._overrides:
            p = pathlib.Path(self._overrides[symbol])
            return p if p.exists() else None

        r = self.resolve_symbol(symbol)
        if r.get("found") and r.get("full_path"):
            p = pathlib.Path(r["full_path"])
            return p if p.exists() else None
        if r.get("found") and r.get("path"):
            p = self.root / r["path"]
            return p if p.exists() else None
        return None

    def route_to_module(self, nc_id: str) -> Any | None:
        """Carrega e retorna modulo por NC-ID. Ex: route_to_module('FR-154') -> KPIEngine"""
        import importlib.util

        fw = self.root / "01_neocortex_framework"
        # Buscar em core/
        core_path = fw / "neocortex" / "core" / f"{nc_id}.py"
        if core_path.exists():
            spec = importlib.util.spec_from_file_location(
                nc_id.replace("-", "_"), str(core_path)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        # Buscar em tools/
        tools_path = fw / "neocortex" / "mcp" / "tools" / f"{nc_id}.py"
        if tools_path.exists():
            spec = importlib.util.spec_from_file_location(
                nc_id.replace("-", "_"), str(tools_path)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        return None


_router = None


def get_router():
    global _router
    if _router is None:
        _router = SemanticRouter()
    return _router
