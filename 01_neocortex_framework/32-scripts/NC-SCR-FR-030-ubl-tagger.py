from __future__ import annotations
"""NC-SCR-FR-030-ubl-tagger.py — Clean + Tag ALL .py/.yaml/.mdc with @UBL + LEXICO."""
import re, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
FW = ROOT / "01_neocortex_framework"
LOBES = ROOT / "02_memory_lobes"
EXCLUDE = {"__pycache__", "99-archive", ".neocortex", "node_modules", ".git", ".opencode", "98-research", "03_external"}
NON_NC = {"config.py", "__init__.py", "server.py", "sub_server.py", "errors.py",
          "mdc_loader.py", "mcp.json", "opencode.json", "pyproject.toml", "pyrightconfig.json", "requirements.txt"}

stats = {"tagged": 0, "skipped": 0, "errors": 0}

def extract_ncid(fname: str) -> str | None:
    m = re.match(r"^(NC-(?:[A-Z]+-){1,2}\d+)", fname)
    return m.group(1) if m else None

def generate_ubl(ncid: str | None, path: str) -> str:
    if ncid:
        parts = ncid.split("-")
        symbol = f"@{parts[1]}-{parts[2]}" if len(parts) >= 3 else f"@{ncid}"
    else:
        symbol = "@SYSTEM"
    tags = set()
    if "core/services" in path: tags.add("#SERVICES")
    elif "core/hooks" in path: tags.add("#HOOKS")
    elif "core/utils" in path: tags.add("#UTILS")
    elif "core/" in path: tags.add("#CORE")
    if "mcp/tools" in path: tags.add("#TOOLS")
    elif "mcp" in path: tags.add("#MCP")
    if "infra/llm" in path: tags.add("#LLM")
    elif "infra" in path: tags.add("#INFRA")
    if "repositories" in path: tags.add("#REPOS")
    if "32-scripts" in path: tags.add("#SCRIPTS")
    if "33-tests" in path: tags.add("#TESTS")
    if "agent" in path: tags.add("#AGENT")
    if "memory_lobes" in path: tags.add("#LOBES")
    if "tickets" in path: tags.add("#TICKETS")
    if "agent-config" in path: tags.add("#CONFIG")
    if "boot" in path: tags.add("#BOOT")
    if "audit" in path: tags.add("#AUDIT")
    if "23-docs" in path: tags.add("#DOCS")
    return f"@UBL {symbol} | LEXICO: {' '.join(sorted(tags)) if tags else '#SYSTEM'}"

def clean_py(content: str) -> str:
    content = re.sub(r'""".*?_genealogy:.*?---\n"""\n?', '', content, flags=re.DOTALL)
    content = re.sub(r'"""---\n@Module.*?---\n"""\n?', '', content, flags=re.DOTALL)
    content = re.sub(r'(?ms)^"""---.*?---"""\n\n"""---.*?---"""\n', '', content)
    content = re.sub(r'(?ms)Funde:.*?Actions:\n.*?"""\n', '"""\n', content)
    return content.strip() + "\n"

def has_ubl(content: str) -> bool:
    return bool(re.search(r"@UBL\s|LEXICO:\s*#", content[:800]))

def tag_py(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if has_ubl(content):
        stats["skipped"] += 1
        return False
    content = clean_py(content)
    ncid = extract_ncid(filepath.name)
    if ncid is None and filepath.name in NON_NC:
        stats["skipped"] += 1
        return False
    ubl = generate_ubl(ncid, str(filepath.parent))
    header = f"# @UBL {ubl}\n"
    lines = content.split("\n")
    future_idx = -1
    for i, line in enumerate(lines[:10]):
        if line.strip().startswith("from __future__"):
            future_idx = i
            break
    if future_idx >= 0:
        lines.insert(future_idx + 1, header)
        new_content = "\n".join(lines)
    else:
        new_content = header + content
    filepath.write_text(new_content, encoding="utf-8")
    stats["tagged"] += 1
    return True

def tag_mdc(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if has_ubl(content) and "NC-READ-HASH" not in content[:100]:
        stats["skipped"] += 1
        return False
    content = re.sub(r'<!-- NC-READ-HASH:.*?-->\n', '', content)
    content = re.sub(r'<!-- DEDUP:.*?-->\n', '', content)
    ncid = extract_ncid(filepath.name)
    ubl = generate_ubl(ncid, str(filepath.parent))
    header = f"<!-- @UBL {ubl} -->\n\n"
    filepath.write_text(header + content, encoding="utf-8")
    stats["tagged"] += 1
    return True

def tag_yaml(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if has_ubl(content) or content.startswith("# @UBL"):
        stats["skipped"] += 1
        return False
    ncid = extract_ncid(filepath.name)
    if ncid is None:
        stats["skipped"] += 1
        return False
    ubl = generate_ubl(ncid, str(filepath.parent))
    filepath.write_text(f"# @UBL {ubl}\n" + content, encoding="utf-8")
    stats["tagged"] += 1
    return True

def main():
    py_files = [f for f in FW.rglob("*.py") if not any(ex in str(f) for ex in EXCLUDE)]
    mdc_files = [f for f in LOBES.rglob("*.mdc") if not any(ex in str(f) for ex in EXCLUDE)]
    yml_files = [f for f in ROOT.rglob("*.yaml") if not any(ex in str(f) for ex in EXCLUDE) and "node_modules" not in str(f) and "98-research" not in str(f) and "03_external" not in str(f) and ".git" not in str(f) and ".claude" not in str(f)]

    for fp in py_files:
        try: tag_py(fp)
        except Exception as e: stats["errors"] += 1; print(f"  PY ERR: {fp.name}")
    print(f".py: {stats['tagged']} tagged / {stats['skipped']} skipped")

    for fp in mdc_files:
        try: tag_mdc(fp)
        except Exception as e: stats["errors"] += 1; print(f"  MDC ERR: {fp.name}")
    print(f".mdc: {stats['tagged']} tagged / {stats['skipped']} skipped")

    for fp in yml_files:
        try: tag_yaml(fp)
        except Exception as e: stats["errors"] += 1; print(f"  YAML ERR: {fp.name}")
    print(f".yaml: {stats['tagged']} tagged / {stats['skipped']} skipped")

    # Validate
    fails = 0
    for f in py_files[:50]:
        if f.name in NON_NC or f.name == "__init__.py":
            continue
        r = subprocess.run(["python", "-m", "py_compile", str(f)], capture_output=True, text=True)
        if r.returncode != 0:
            fails += 1
    print(f"\npy_compile spot check: {50-fails}/50 OK")
    print(f"Total: {stats['tagged']} tagged | {stats['skipped']} skipped | {stats['errors']} errors")

if __name__ == "__main__":
    main()
