# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.675248'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-013-validate-file
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.675248'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-013-validate-file

---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.675248'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-013-validate-file
related_ssot:
  - NC-CFG-FR-001-base
  - NC-SCR-FR-013
  - NC-SVC-FR-010-coordinator
  - NC-SVC-FR-003-save-point
  - NC-CFG-FR-003-env-validator
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-013-validate-file.py
UTIL  Script de validacao completa de arquivos Python do NeoCortex

Uso:
    python NC-SCR-FR-013-validate-file.py                    # valida todo o projeto
    python NC-SCR-FR-013-validate-file.py caminho/arquivo.py # valida arquivo especifico
    python NC-SCR-FR-013-validate-file.py --r11-fix          # substitui print() por logger (R11)
    python NC-SCR-FR-013-validate-file.py --f811-fix FILE    # remove redef. register_tool (F811)
    python NC-SCR-FR-013-validate-file.py --missing-map      # mapeia arquivos ausentes

Executa em ordem: py_compile -> ruff check --fix -> bandit (se disponivel)
Gera relatorio de erros e summary.

Changelog:
    2026-04-13 v2.0 - Adicionados: --r11-fix, --f811-fix, --missing-map, --zone, --dry-run
    2026-04-13 v1.0 - Versao inicial
"""
import argparse
import ast
import json
import os
import py_compile
import re
import subprocess
import sys
from pathlib import Path

logger_module = __import__("logging")
logger = logger_module.getLogger(__name__)

BASE = Path(__file__).parent.parent  # raiz do projeto dentro de 01_neocortex_framework

EXCLUDE_DIRS = {"__pycache__", ".venv", "DIR-ARC-FR-001-archive-main", "DIR-BAK-FR-001-backup-main"}
EXCLUDE_PATTERNS = ["backup_root"]

ZONE_MAP = {
    "A": ["neocortex/core"],
    "B": ["neocortex/mcp/tools"],
    "C": ["neocortex/mcp/tools", "scripts", "DIR-MCP-FR-001"],
}

# Arquivos que o Agente Zona A reportou como ausentes (mapa canonico)
EXPECTED_FILES = {
    "NC-CFG-FR-001-base.py": ["neocortex/core/config", "neocortex/core"],
    "NC-CFG-FR-003-env-validator.py": ["neocortex/core/config"],
    "NC-SVC-FR-003-save-point.py": ["neocortex/core/services"],
    "NC-SVC-FR-010-coordinator.py": ["neocortex/core/services"],
}


#  coleta de arquivos

def collect_files(root: Path, zone: str = "") -> list:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if any(p in dirpath for p in EXCLUDE_PATTERNS):
            continue
        for f in filenames:
            if f.endswith(".py"):
                files.append(Path(dirpath) / f)
    if zone:
        dirs = ZONE_MAP.get(zone.upper(), [])
        files = [f for f in files if any(d in str(f).replace("\\", "/") for d in dirs)]
    return sorted(files)


#  validacao individual

def check_compile(filepath: Path) -> tuple:
    try:
        py_compile.compile(str(filepath), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)


def check_ruff(filepath: Path) -> tuple:
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(filepath)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return True, None
    return False, (result.stdout or result.stderr or "").strip()


def fix_ruff(filepath: Path) -> int:
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--fix", str(filepath)],
        capture_output=True, text=True
    )
    return result.returncode


def check_bandit(filepath: Path) -> tuple:
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-q", str(filepath),
         "--severity-level", "MEDIUM", "--confidence-level", "MEDIUM"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return True, None
    return False, (result.stdout or "").strip()[:500]


def validate_file(filepath: Path, auto_fix: bool = True, run_bandit: bool = False) -> dict:
    rel = str(filepath).replace(str(BASE) + os.sep, "")
    result = {"file": rel, "compile": None, "ruff": None, "bandit": None, "errors": []}

    ok, err = check_compile(filepath)
    result["compile"] = "OK" if ok else f"ERR: {err}"
    if not ok:
        result["errors"].append(f"COMPILE: {err}")
        return result

    ok, err = check_ruff(filepath)
    if not ok and auto_fix:
        fix_ruff(filepath)
        ok2, err2 = check_ruff(filepath)
        result["ruff"] = "OK (auto-fixed)" if ok2 else f"ERR (apos fix): {err2}"
        if not ok2:
            result["errors"].append(f"RUFF: {err2}")
    else:
        result["ruff"] = "OK" if ok else f"ERR: {err}"
        if not ok:
            result["errors"].append(f"RUFF: {err}")

    if run_bandit:
        ok, err = check_bandit(filepath)
        result["bandit"] = "OK" if ok else f"WARN: {err}"

    return result


#  R11-FIX: substituir print() por logger

R11_PRINT_RE = re.compile(r'^(\s*)print\(', re.MULTILINE)
LOGGER_INJECT = "import logging\nlogger = logging.getLogger(__name__)\n"


def r11_fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Substitui print() por logger.info() em um arquivo Python (R11).
    Injeta `import logging / logger = logging.getLogger(__name__)` se nao existir.
    """
    text = filepath.read_text(encoding="utf-8")
    matches = R11_PRINT_RE.findall(text)
    count = len(matches)
    if count == 0:
        return {"file": str(filepath), "changed": False, "print_replaced": 0}

    new_text = R11_PRINT_RE.sub(r'\1logger.info(', text)

    has_logger = "logging.getLogger" in text
    if not has_logger:
        lines = new_text.splitlines(keepends=True)
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")):
                last_import = i
        lines.insert(last_import + 1, LOGGER_INJECT)
        new_text = "".join(lines)

    if not dry_run:
        filepath.write_text(new_text, encoding="utf-8")

    return {
        "file": str(filepath),
        "changed": True,
        "print_replaced": count,
        "logger_injected": not has_logger,
    }


def r11_fix_zone(root: Path, zone: str = "B", dry_run: bool = False) -> list:
    """Aplica R11-fix em todos os arquivos de uma zona e re-valida."""
    files = collect_files(root, zone=zone)
    results = []
    for f in files:
        r = r11_fix_file(f, dry_run=dry_run)
        if r["changed"]:
            results.append(r)
            tag = "[DRY]" if dry_run else "[FIX]"
            print(f"  {tag} R11 {r['print_replaced']}x print->logger: {r['file']}")
    print(f"\n  Total R11 alterados: {len(results)} de {len(files)} arquivos")
    if not dry_run and results:
        print("  Re-validando com ruff...")
        for r in results:
            vr = validate_file(Path(r["file"]), auto_fix=True)
            tag = "OK " if not vr["errors"] else "ERR"
            print(f"    [{tag}] {vr['file']}")
    return results


#  F811-FIX: remover redefinicoes de register_tool

def f811_fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Remove redefinicoes duplicadas de register_tool em um arquivo Python (F811).
    Mantm apenas a ultima definicao de cada funcao.
    """
    text = filepath.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return {"file": str(filepath), "fixed": False, "error": str(e)}

    definitions = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "register_tool"
    ]

    if len(definitions) <= 1:
        return {"file": str(filepath), "fixed": False, "duplicates": 0}

    lines = text.splitlines(keepends=True)
    to_remove = set()
    for fn_node in definitions[:-1]:  # remove todas menos a ultima
        end = fn_node.end_lineno if hasattr(fn_node, "end_lineno") else fn_node.lineno
        for ln in range(fn_node.lineno - 1, end):
            to_remove.add(ln)

    new_lines = [line_str for i, line_str in enumerate(lines) if i not in to_remove]
    new_text = "".join(new_lines)

    if not dry_run:
        filepath.write_text(new_text, encoding="utf-8")

    return {
        "file": str(filepath),
        "fixed": True,
        "duplicates_removed": len(definitions) - 1,
        "kept_at_line": definitions[-1].lineno,
    }


#  MISSING-MAP: mapear arquivos esperados vs presentes

def missing_map(root: Path) -> list:
    """Verifica se arquivos esperados existem (nome exato ou variantes)."""
    results = []
    for expected_name, search_dirs in EXPECTED_FILES.items():
        found = []
        stem_lower = expected_name.replace(".py", "").lower()
        for d in search_dirs:
            search_path = root / d.replace("/", os.sep)
            if not search_path.exists():
                continue
            for f in search_path.glob("*.py"):
                if expected_name == f.name:
                    found.append(f"[EXATO] {f}")
                elif stem_lower in f.name.lower():
                    found.append(f"[VARIANTE] {f.name}")
        status = "OK" if found else "AUSENTE"
        results.append({"expected": expected_name, "status": status, "found": found})
        print(f"  [{status}] {expected_name}")
        for match in found:
            print(f"         {match}")
    return results


#  MAIN

def main():
    parser = argparse.ArgumentParser(description="NC-SCR-FR-013 v2.0: Validate + Fix Python files")
    parser.add_argument("files", nargs="*", help="Arquivos a validar (default: todo o projeto)")
    parser.add_argument("--no-fix",       action="store_true", help="Nao aplicar ruff --fix")
    parser.add_argument("--bandit",       action="store_true", help="Incluir bandit security check")
    parser.add_argument("--report",       type=str, default=None, help="Salvar relatorio em arquivo .json")
    parser.add_argument("--zone",         type=str, default="", help="Filtrar por zona: A, B ou C")
    parser.add_argument("--dry-run",      action="store_true", help="Simular sem escrever (r11/f811)")
    # Novos modos
    parser.add_argument("--r11-fix",      action="store_true", help="[R11] Substituir print() por logger em massa")
    parser.add_argument("--r11-zone",     type=str, default="B", help="Zona para --r11-fix (default: B)")
    parser.add_argument("--f811-fix",     type=str, default="", metavar="FILE",
                        help="[F811] Remover redefinicoes register_tool em FILE")
    parser.add_argument("--missing-map",  action="store_true", help="Mapear arquivos ausentes vs esperados")
    args = parser.parse_args()

    #  Modo: missing-map
    if args.missing_map:
        print("=== NC-SCR-FR-013 v2.0 | MISSING-MAP ===")
        missing_map(BASE)
        return 0

    #  Modo: R11 mass fix
    if args.r11_fix:
        print(f"=== NC-SCR-FR-013 v2.0 | R11-FIX | zona={args.r11_zone} | dry={args.dry_run} ===")
        r11_fix_zone(BASE, zone=args.r11_zone, dry_run=args.dry_run)
        return 0

    #  Modo: F811 fix
    if args.f811_fix:
        fp = Path(args.f811_fix)
        if not fp.exists():
            fp = BASE / args.f811_fix
        print(f"=== NC-SCR-FR-013 v2.0 | F811-FIX | {fp} ===")
        result = f811_fix_file(fp, dry_run=args.dry_run)
        print(f"  Resultado: {result}")
        if result.get("fixed") and not args.dry_run:
            vr = validate_file(fp, auto_fix=True)
            print(f"  Pos-fix ruff: {vr['ruff']}")
        return 0

    #  Modo padrao: validate
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = collect_files(BASE, zone=args.zone)

    print(f"=== NC-SCR-FR-013 v2.0 | {len(files)} arquivos | zona={args.zone or 'ALL'} ===")

    results = []
    errors_found = []

    for f in files:
        r = validate_file(f, auto_fix=not args.no_fix, run_bandit=args.bandit)
        results.append(r)
        status = "OK " if not r["errors"] else "ERR"
        ruff_s = r["ruff"] or "SKIP"
        print(f"  [{status}] {r['file']:<70} compile={r['compile']} | ruff={ruff_s}")
        if r["errors"]:
            errors_found.append(r)

    print("\n=== SUMMARY ===")
    print(f"Total: {len(files)} | OK: {len(files) - len(errors_found)} | ERR: {len(errors_found)}")

    if errors_found:
        print("\n=== ERROS DETALHADOS ===")
        for r in errors_found:
            print(f"  [ERR] {r['file']}")
            for e in r["errors"]:
                print(f"    {e[:200]}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as fout:
            json.dump({"total": len(files), "errors": len(errors_found), "details": results}, fout, indent=2)
        print(f"\nRelatorio salvo: {args.report}")

    return 1 if errors_found else 0


if __name__ == "__main__":
    sys.exit(main())
