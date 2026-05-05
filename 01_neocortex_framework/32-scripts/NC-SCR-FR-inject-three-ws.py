"""---
NC-SCR-FR-inject-three-ws.py — Injeta ## What / ## Why / ## Where em todo arquivo NC-
Conceito juridico: Auto de Infração (Processo Administrativo)
Integra com: @POPULATE pipeline, ThreeWEngine (FR-151)
---
"""
import pathlib, sys, os, re, shutil
from datetime import datetime

ROOT = pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[2] if __file__ else pathlib.Path.cwd().parents[2] if "Q" in str(pathlib.Path.cwd()) else pathlib.Path(__file__).parents[3]))

FW = ROOT / "01_neocortex_framework"
LOBES = ROOT / "02_memory_lobes"
DRY_RUN = "--apply" not in sys.argv

STATS = {"scanned": 0, "injected": 0, "skipped_has_www": 0, "skipped_no_docstring": 0, "errors": 0}


def extract_what(content: str, name: str) -> str:
    m = re.search(r'\"\"\"---\n(.+?)\n---', content, re.DOTALL)
    if m:
        return m.group(1).strip()[:200]
    m2 = re.search(r'\"\"\"(.+?)\"\"\"', content, re.DOTALL)
    if m2:
        return m2.group(1).strip().split("\n")[0][:200]
    return f"Módulo: {name}"


def extract_why(content: str, file_path: pathlib.Path) -> str:
    m = re.search(r'# (?:porque|adicionado para|fixes|resolve|causa raiz|implementa)[\s:]*(.+)', content, re.IGNORECASE)
    if m:
        return m.group(1).strip()[:150]
    return f"Criado em {datetime.fromtimestamp(file_path.stat().st_ctime):%Y-%m-%d} — arquivo do ecossistema NeoCortex"


def extract_where(file_path: pathlib.Path) -> str:
    try:
        rel = file_path.relative_to(ROOT)
    except ValueError:
        rel = file_path
    parts = rel.parts
    if "neocortex" in parts:
        idx = parts.index("neocortex")
        return "/".join(parts[idx:idx + 3])
    if "02_memory_lobes" in parts:
        idx = parts.index("02_memory_lobes")
        return "/".join(parts[idx:idx + 2])
    return "/".join(parts[:3])


def has_three_ws(content: str) -> bool:
    return bool(re.search(r'## What\b', content, re.IGNORECASE))


def inject_three_ws(file_path: pathlib.Path, ext: str) -> bool:
    try:
        original = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        STATS["errors"] += 1
        return False

    STATS["scanned"] += 1

    if has_three_ws(original):
        STATS["skipped_has_www"] += 1
        return False

    what = extract_what(original, file_path.stem.replace("-", " "))
    why = extract_why(original, file_path)
    where = extract_where(file_path)

    if not what or (not original.strip()):
        STATS["skipped_no_docstring"] += 1
        return False

    # Build injection block
    if ext == ".py":
        block = f'"""---\n{what}\n' f'---\n"""\n'
        # Inject after existing triple-quote or at top
        if original.strip().startswith('"""'):
            # Replace first docstring
            injected = re.sub(
                r'"""(.+?)"""',
                block,
                original,
                count=1,
                flags=re.DOTALL
            )
        elif original.strip().startswith("#"):
            # Insert after first comment block
            lines = original.split("\n")
            idx = 0
            for i, l in enumerate(lines):
                if not l.strip().startswith("#") and l.strip():
                    idx = i
                    break
            lines.insert(idx, block)
            injected = "\n".join(lines)
        else:
            injected = block + "\n" + original
    elif ext in (".mdc", ".md"):
        block = (
            f"<!-- 3 W's Auto-Injection -->\n"
            f"## What\n{what}\n\n"
            f"## Why\n{why}\n\n"
            f"## Where\n{where}\n\n"
            f"---\n"
        )
        # Insert after YAML header if present
        if original.strip().startswith("---"):
            parts = original.split("---", 2)
            if len(parts) >= 3:
                injected = f"---{parts[1]}---\n\n{block}{parts[2]}"
            else:
                injected = block + "\n" + original
        else:
            injected = block + "\n" + original
    elif ext in (".yaml", ".yml"):
        block = (
            f"# ── 3 W's (Auto de Infração) ──\n"
            f"# What: {what}\n"
            f"# Why:  {why}\n"
            f"# Where: {where}\n"
            f"\n"
        )
        # Skip pure config files (avoid breaking YAML syntax)
        if re.search(r'^(?:apiVersion|kind:|metadata:|spec:)', original.strip(), re.MULTILINE):
            STATS["skipped_has_www"] += 1
            return False
        if original.strip().startswith("#"):
            injected = block + original
        else:
            injected = block + original
    else:
        return False

    if DRY_RUN:
        STATS["injected"] += 1
        return True

    # Backup + write
    bak = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, bak)
    file_path.write_text(injected, encoding="utf-8")
    bak.unlink()
    STATS["injected"] += 1
    return True


def scan_and_inject():
    targets = []
    if FW.exists():
        targets.extend(FW.rglob("*.py"))
        targets.extend(FW.rglob("*.yaml"))
        targets.extend(FW.rglob("*.yml"))
    if LOBES.exists():
        targets.extend(LOBES.rglob("*.mdc"))
        targets.extend(LOBES.rglob("*.md"))

    # Skip __pycache__, .git, node_modules
    targets = [t for t in targets if "__pycache__" not in str(t) and ".git" not in str(t) and "node_modules" not in str(t)]

    print(f"[3-W's Injector] Scanning {len(targets)} files {'(DRY RUN)' if DRY_RUN else '(APPLY)'}")

    for fp in sorted(targets):
        inject_three_ws(fp, fp.suffix)

    print(f"  Scanned: {STATS['scanned']}")
    print(f"  Injected: {STATS['injected']}")
    print(f"  Skipped (has 3 W's): {STATS['skipped_has_www']}")
    print(f"  Skipped (no docstring): {STATS['skipped_no_docstring']}")
    print(f"  Errors: {STATS['errors']}")

    if DRY_RUN:
        print("  ⚠ DRY RUN — use --apply to write")

    return STATS


if __name__ == "__main__":
    scan_and_inject()
