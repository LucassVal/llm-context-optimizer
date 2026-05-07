# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)


if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.618078'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-003-manifest-factory
related_ssot:
  - NC-CFG-FR-001
  - NC-NAM-FR-001-naming-convention
  - NC-NAM-FR-001
  - '@NC-NAM-FR-001'
  - NC-MAN-FR-001-project-manifest
  - NC-TOOL-FR-001-cortex
  - NC-TOOL-FR-020
  - NC-CORE-FR-014
  - NC-CORE-FR-022
  - NC-SEC-FR-001
  - NC-CFG-FR-001-agent-policy-template
  - NC-BOOT-FR-001-system-manifest
  - NC-SCR-FR-003
  - NC-TLM-FR-001
  - NC-MAN-FR-001
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-003-manifest-factory.py
Manifest Factory  Escaneia TODO o projeto e gera manifesto compacto.

Uso:
    python NC-SCR-FR-003-manifest-factory.py [--output <path>] [--format json|yaml|md|all]

Sada (padro: DIR-DOC-FR-001-docs-main/NC-MAN-FR-001-project-manifest.json):
  - JSON completo (.json)   usado por IAs via API (1 read = contexto completo)
  - Markdown resumo (.md)   legvel por humanos / PR description
  - JSONL por arquivo       busca granular

Estrutura do manifesto:
  {
    "meta": { version, generated_at, project_root, total_files, total_dirs, ... },
    "ssot_files": [ { nc_id, path, type, size, summary } ],
    "structure": { "dir_path": [ file_entries ] },
    "nc_index": { "NC-CORE-FR-014": { path, type, ... } },
    "boot_context": "string compacta para bootstrap de IA"
  }
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

#  Config
PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # 01_neocortex_framework
sys.path.append(str(PROJECT_ROOT))
from neocortex.core.file_utils import get_lobes_path

OUTPUT_DIR   = PROJECT_ROOT / "DIR-DOC-FR-001-docs-main"
OUTPUT_JSON  = OUTPUT_DIR / "NC-MAN-FR-001-project-manifest.json"
OUTPUT_MD    = OUTPUT_DIR / "NC-MAN-FR-001-project-manifest.md"
OUTPUT_JSONL = OUTPUT_DIR / "NC-MAN-FR-001-project-manifest.jsonl"

# Diretrios/arquivos ignorados (R08: sem *.db, *.wal, lobes/, __pycache__/)
IGNORE_DIRS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    ".mypy_cache", ".pytest_cache", "lobes",
    "DIR-BAK-FR-001-backup-main", "DIR-ARC-FR-001-archive-main",
}
IGNORE_EXTENSIONS = {".db", ".wal", ".log", ".pyc", ".pyo", ".egg-info"}
IGNORE_PATTERNS   = {"*.db-wal", "*.db-shm"}

# Extenses com contedo relevante para IA
IMPORTANT_EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".cfg", ".bat", ".ps1", ".mdc"}

# NC- category descriptions para inferncia automtica
NC_DESCRIPTIONS = {
    "NC-CORE": "Servio core do framework",
    "NC-TOOL": "Ferramenta MCP exposta",
    "NC-SCR":  "Script utilitrio",
    "NC-CFG":  "Arquivo de configurao",
    "NC-DOC":  "Documentao",
    "NC-NAM":  "Conveno de nomenclatura (SSOT)",
    "NC-TODO": "Roadmap / tickets",
    "NC-SEC":  "Segurana e locks",
    "NC-BOOT": "Manifest de boot",
    "NC-MAN":  "Manifesto de projeto",
    "NC-TLM":  "Tool manifest (ndice de ferramentas)",
    "NC-LBE":  "Lobo de memria",
    "NC-MCP":  "Servidor MCP",
    "NC-RULE": "Regra de governana",
    "NC-INFRA":"Infraestrutura",
    "NC-TEST": "Testes",
    "NC-LOG":  "Logs de auditoria",
    "NC-SOP":  "Procedimento operacional",
    "DIR-DOC": "Diretrio de documentao",
    "DIR-BOOT":"Diretrio de boot",
    "DIR-BAK": "Diretrio de backup",
    "DIR-ARC": "Diretrio de arquivo morto",
    "DIR-TMP": "Diretrio temporrio",
}


def _should_ignore(path: Path) -> bool:
    if path.name in IGNORE_DIRS or path.name.startswith("."):
        return True
    if path.is_file():
        if path.suffix in IGNORE_EXTENSIONS:
            return True
        for p in IGNORE_PATTERNS:
            if path.match(p):
                return True
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    return False


def _infer_nc_desc(name: str) -> str:
    """Infere descrio a partir do prefixo NC-."""
    for prefix, desc in NC_DESCRIPTIONS.items():
        if name.upper().startswith(prefix):
            return desc
    return ""


def _file_hash(path: Path, length=8) -> str:
    try:
        h = hashlib.md5(path.read_bytes()).hexdigest()
        return h[:length]
    except Exception:
        return "????????"


def _file_entry(path: Path, rel_root: Path) -> dict:
    rel = str(path.relative_to(rel_root)).replace("\\", "/")
    stat = path.stat()
    entry = {
        "path": rel,
        "name": path.name,
        "ext": path.suffix,
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 1),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "nc_id": path.stem if path.stem.startswith("NC-") or path.stem.startswith("DIR-") else "",
        "nc_desc": _infer_nc_desc(path.name),
        "is_ssot": any(k in path.name for k in ["NC-NAM-", "NC-BOOT-", "NC-TODO-", "NC-SEC-FR-001"]),
        "hash": _file_hash(path),
        "important": path.suffix in IMPORTANT_EXTENSIONS,
    }
    # Mini-summary: primeira linha de docstring ou comentrio
    if path.suffix in {".py", ".md", ".yaml", ".yml"} and stat.st_size < 200_000:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line in lines[:10]:
                stripped = line.strip().lstrip("#").lstrip('"').lstrip("'").strip()
                if len(stripped) > 20 and not stripped.startswith("import") and not stripped.startswith("from"):
                    entry["summary"] = stripped[:120]
                    break
        except Exception:
            pass
    return entry


#  System profile scanners

def _scan_mcp_tools(root: Path) -> list:
    """Escaneia neocortex/mcp/tools/ e extrai metadata de cada NC-TOOL."""
    tools_dir = root / "neocortex" / "mcp" / "tools"
    results = []
    if not tools_dir.exists():
        return results

    # Categorias das super-tools (NC-TOOL-FR-020)
    CATEGORIES = {
        **dict.fromkeys(["001","009","018","006","007","014"], "memory"),
        **dict.fromkeys(["004","012","031","008","011"],         "session"),
        **dict.fromkeys(["002","017","016","010","003"],         "agents"),
        **dict.fromkeys(["005","015","013"],                      "config"),
        **dict.fromkeys(["000","019"],                             "knowledge"),
        **dict.fromkeys(["020"],                                   "hub"),
    }

    for py in sorted(tools_dir.glob("NC-TOOL-FR-*.py")):
        nc_id = py.stem  # ex: NC-TOOL-FR-001-cortex
        parts = nc_id.split("-")
        num = parts[3] if len(parts) > 3 else "000"
        cat = CATEGORIES.get(num, "other")
        doc = ""
        try:
            lines = py.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line in lines[:15]:
                s = line.strip().strip('"').strip("'").strip()
                if len(s) > 20 and not s.startswith(("#", "from", "import", "NC-")):
                    doc = s[:120]
                    break
        except Exception:
            pass
        results.append({
            "nc_id": nc_id,
            "file": py.name,
            "category": cat,
            "num": num,
            "doc": doc,
            "size_kb": round(py.stat().st_size / 1024, 1),
        })
    return results


def _scan_lobes(root: Path) -> list:
    """Escaneia memory_lobes/ e extrai metadata de cada lobe."""
    lobes_root = get_lobes_path()
    results = []
    if not lobes_root.exists():
        return results

    for lobe_dir in sorted(lobes_root.iterdir()):
        if not lobe_dir.is_dir():
            continue
        lobe_files = list(lobe_dir.glob("*.mdc")) + list(lobe_dir.glob("*.md"))
        size_kb = sum(f.stat().st_size for f in lobe_dir.rglob("*") if f.is_file()) / 1024
        summary = ""
        if lobe_files:
            try:
                lines = lobe_files[0].read_text(encoding="utf-8", errors="ignore").splitlines()
                for line in lines[:5]:
                    s = line.strip().lstrip("#").strip()
                    if len(s) > 15:
                        summary = s[:100]
                        break
            except Exception:
                pass
        results.append({
            "name": lobe_dir.name,
            "path": str(lobe_dir.relative_to(root.parent)).replace("\\", "/"),
            "files": len(lobe_files),
            "size_kb": round(size_kb, 1),
            "summary": summary,
        })
    return results


def _scan_governance(root: Path) -> list:
    """Verifica os 8 padres de governana e retorna status atual."""
    standards = [
        ("lock_guard",    "HIGH",  "Atomic Locks LockGuard",     "neocortex/core",   "NC-CORE-FR-014*"),
        ("policy_yaml",   "HIGH",  "Policy YAML (PRE-1)",        "DIR-DOC-FR-001-docs-main", "NC-CFG-FR-001*"),
        ("mentor_mode",   "HIGH",  "Mentor mode STEP 0",         "neocortex/mcp",    "sub_server.py"),
        ("audit_trail",   "HIGH",  "Audit Trail SEC-401",        "neocortex/core",   "security_service.py"),
        ("save_point",    "HIGH",  "Save Point STEP -1",         "neocortex/core",   "NC-CORE-FR-022*"),
        ("ssot_naming",   "MED",   "SSOT Naming @NC-NAM-FR-001", "DIR-DOC-FR-001-docs-main", "NC-NAM-FR-001*"),
        ("pulse",         "MED",   "PulseScheduler ativo",       "neocortex/core",   "*pulse*scheduler*.py"),
        ("tool_manifest", "LOW",   "NC-TLM-FR-001 presente",     "DIR-DOC-FR-001-docs-main", "NC-TLM-FR-001*"),
    ]
    results = []
    for key, level, label, sub_dir, pattern in standards:
        search_dir = root / sub_dir
        found = list(search_dir.glob(pattern)) if search_dir.exists() else []
        # Verificaes especiais
        detail = ""
        if found:
            detail = found[0].name
            # Para mentor_mode: verificar keyword no arquivo
            if key == "mentor_mode":
                try:
                    txt = found[0].read_text(encoding="utf-8", errors="ignore")
                    found = [found[0]] if "mentor_step_0" in txt else []
                    detail = "mentor_step_0 present" if found else "mentor_step_0 MISSING"
                except Exception:
                    found = []
            # Para audit_trail: verificar deny_by_default_sec401
            if key == "audit_trail":
                try:
                    txt = found[0].read_text(encoding="utf-8", errors="ignore")
                    found = [found[0]] if "deny_by_default_sec401" in txt else []
                    detail = "deny_by_default_sec401 FIXADO" if found else "SEC-401 ABERTO"
                except Exception:
                    found = []
        results.append({
            "key": key,
            "level": level,
            "label": label,
            "status": "OK" if found else "MISSING",
            "detail": detail,
        })
    return results


def _build_system_profile(root: Path) -> dict:
    """Consolida o perfil completo do sistema para bootstrap de IA."""
    mcp_tools = _scan_mcp_tools(root)
    lobes = _scan_lobes(root)
    governance = _scan_governance(root)

    # Agrupar tools por categoria
    by_category: dict = {}
    for t in mcp_tools:
        by_category.setdefault(t["category"], []).append(t["nc_id"])

    total_ok = sum(1 for g in governance if g["status"] == "OK")
    total_gov = len(governance)

    return {
        "mcp_tools": {
            "total": len(mcp_tools),
            "by_category": by_category,
            "entries": mcp_tools,
        },
        "lobes": {
            "total": len(lobes),
            "entries": lobes,
        },
        "governance": {
            "score": f"{total_ok}/{total_gov}",
            "standards": governance,
        },
        "boot_sequence": [
            "NC-BOOT-FR-001-system-manifest.md",
            "NC-CFG-FR-001-agent-policy-template.yaml",
            "NC-NAM-FR-001-naming-convention.md",
            "NC-MAN-FR-001-project-manifest.json",
        ],
    }


def scan_project(root: Path) -> dict:
    """Escaneia recursivamente e retorna estrutura de manifesto."""
    print(f"[Factory] Escaneando: {root}")

    total_files = 0
    total_dirs  = 0
    total_size  = 0
    ssot_files  = []
    structure   = {}
    nc_index    = {}

    for dirpath, dirnames, filenames in os.walk(root):
        # Filtrar diretrios ignorados in-place (O(n) nico pass)
        dirnames[:] = [d for d in dirnames
                       if not _should_ignore(Path(dirpath) / d)]
        dirnames.sort()

        dp = Path(dirpath)
        if _should_ignore(dp):
            continue

        rel_dir = str(dp.relative_to(root)).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = "."
        total_dirs += 1
        dir_entries = []

        for fname in sorted(filenames):
            fp = dp / fname
            if _should_ignore(fp):
                continue

            entry = _file_entry(fp, root)
            total_files += 1
            total_size += entry["size_bytes"]
            dir_entries.append(entry)

            if entry["nc_id"]:
                nc_index[entry["nc_id"]] = {
                    "path": entry["path"],
                    "size_kb": entry["size_kb"],
                    "nc_desc": entry["nc_desc"],
                    "is_ssot": entry["is_ssot"],
                }

            if entry["is_ssot"]:
                ssot_files.append(entry)

        if dir_entries:
            structure[rel_dir] = dir_entries

    # Boot context  string compacta para enviar para IA
    boot_lines = [
        "# NeoCortex Framework  Project Manifest",
        f"# generated: {datetime.now().isoformat()} | files: {total_files} | size: {total_size/1024/1024:.1f}MB",
        "",
        "## SSOT Critical Files",
    ]
    for sf in ssot_files:
        boot_lines.append(f"  {sf['nc_id']:30s}  {sf['path']}")

    boot_lines.append("\n## NC- Index (all named files)")
    for nc_id, info in sorted(nc_index.items()):
        boot_lines.append(f"  {nc_id:35s} {info['path']}")

    boot_lines.append("\n## Directory Structure")
    for dpath, entries in structure.items():
        important = [e for e in entries if e["important"]]
        if important:
            boot_lines.append(f"  {dpath}/")
            for e in important[:8]:
                boot_lines.append(f"    {'[SSOT]' if e['is_ssot'] else '      '} {e['name']}")

    boot_context = "\n".join(boot_lines)

    # System profile  MCP tools, lobes, governana
    system_profile = _build_system_profile(root)
    gov_score = system_profile["governance"]["score"]

    # Adicionar system_profile ao boot_context
    boot_lines.append("\n## System Profile")
    boot_lines.append(f"  MCP Tools: {system_profile['mcp_tools']['total']} | Lobes: {system_profile['lobes']['total']} | Governance: {gov_score}")
    boot_lines.append("  Tool Categories: " + ", ".join(
        f"{cat}({len(ids)})" for cat, ids in system_profile["mcp_tools"]["by_category"].items()
    ))
    if system_profile["lobes"]["entries"]:
        boot_lines.append("  Active Lobes: " + ", ".join(l["name"] for l in system_profile["lobes"]["entries"]))
    boot_lines.append("  Boot Sequence: " + "  ".join(system_profile["boot_sequence"]))
    boot_context = "\n".join(boot_lines)

    return {
        "meta": {
            "version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "generator": "NC-SCR-FR-003-manifest-factory.py",
            "project_root": str(root),
            "total_files": total_files,
            "total_dirs": total_dirs,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "ssot_count": len(ssot_files),
            "nc_named_count": len(nc_index),
        },
        "system_profile": system_profile,
        "ssot_files": ssot_files,
        "nc_index": nc_index,
        "structure": structure,
        "boot_context": boot_context,
    }


def write_json(manifest: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Factory] JSON  {path}  ({path.stat().st_size/1024:.0f} KB)")


def write_jsonl(manifest: dict, path: Path):
    """JSONL com 1 entrada por arquivo  para busca granular."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for entries in manifest["structure"].values():
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[Factory] JSONL  {path}  ({path.stat().st_size/1024:.0f} KB)")


def write_markdown(manifest: dict, path: Path):
    meta = manifest["meta"]
    lines = [
        "# NC-MAN-FR-001  Project Manifest",
        f"> Generated: `{meta['generated_at']}`  |  Generator: `{meta['generator']}`",
        f"> Files: **{meta['total_files']}**  |  Dirs: **{meta['total_dirs']}**  ",
        f"> Size: **{meta['total_size_mb']} MB**  |  NC-named: **{meta['nc_named_count']}**",
        "",
        "##  SSOT Critical Files",
        "| NC-ID | Path | Size |",
        "|---|---|---|",
    ]
    for sf in manifest["ssot_files"]:
        lines.append(f"| `{sf['nc_id']}` | `{sf['path']}` | {sf['size_kb']} KB |")

    lines += [
        "",
        "##  NC- Index (todos os arquivos com prefixo NC-)",
        "| NC-ID | Path | Descrio | Size |",
        "|---|---|---|---|",
    ]
    for nc_id, info in sorted(manifest["nc_index"].items()):
        ssot_mark = "" if info["is_ssot"] else ""
        lines.append(f"| `{nc_id}` | `{info['path']}` | {info['nc_desc']} {ssot_mark} | {info['size_kb']} KB |")

    lines += ["", "##  Estrutura de Diretrios", ""]
    for dpath, entries in manifest["structure"].items():
        important = [e for e in entries if e["important"]]
        if important:
            lines.append(f"### `{dpath}/`")
            lines.append("| Arquivo | Tipo | Size | Hash |")
            lines.append("|---|---|---|---|")
            for e in important:
                ssot = " " if e["is_ssot"] else ""
                lines.append(f"| {ssot}`{e['name']}` | `{e['ext']}` | {e['size_kb']} KB | `{e['hash']}` |")
            lines.append("")

    lines += [
        "##  Boot Context (para enviar a nova IA)",
        "```",
        manifest["boot_context"],
        "```",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[Factory] MD   {path}  ({path.stat().st_size/1024:.0f} KB)")


def run(fmt="all", output_dir=None):
    """Entry point programtico (chamado via MCP tool ou CLI)."""
    root = PROJECT_ROOT
    out  = Path(output_dir) if output_dir else OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    manifest = scan_project(root)

    if fmt in ("json", "all"):
        write_json(manifest, out / "NC-MAN-FR-001-project-manifest.json")
    if fmt in ("jsonl", "all"):
        write_jsonl(manifest, out / "NC-MAN-FR-001-project-manifest.jsonl")
    if fmt in ("md", "all"):
        write_markdown(manifest, out / "NC-MAN-FR-001-project-manifest.md")

    print(f"\n[Factory] DONE  {manifest['meta']['total_files']} files, "
          f"{manifest['meta']['nc_named_count']} NC-named, "
          f"{manifest['meta']['total_size_mb']} MB")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NC-SCR-FR-003 Manifest Factory")
    parser.add_argument("--format", choices=["json", "jsonl", "md", "all"], default="all",
                        help="Formato de sada (padro: all)")
    parser.add_argument("--output", type=str, default=None,
                        help="Diretrio de sada (padro: DIR-DOC-FR-001-docs-main/)")
    args = parser.parse_args()
    run(fmt=args.format, output_dir=args.output)
