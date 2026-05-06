#!/usr/bin/env python3
"""Regenerate LEXICO (NC-LEXICO-LATEST.json) from disk scan.
DDD chain: Constitution -> ULQ-TAG-INDEX -> LEXICO -> MANIFEST -> BOOT
"""
import json, hashlib, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent if "__file__" in dir() else Path(".")
FW = ROOT / "01_neocortex_framework"
LEXICO_PATH = FW / ".neocortex" / "lexico" / "NC-LEXICO-LATEST.json"

# ── CATEGORIZATION ────────────────────────────────────
def categorize(rel_path: str, fname: str) -> tuple[str, str]:
    """Return (category, symbol_prefix)."""
    if "/core/services/" in rel_path:
        return "services", "NC-SVC-FR"
    if "/core/hooks/" in rel_path:
        return "hooks", "NC-HK-FR"
    if "/core/utils/" in rel_path:
        return "utilities", "NC-UTL-FR"
    if "/core/" in rel_path:
        return "engines", "NC-CORE-FR"
    if "/mcp/tools/" in rel_path:
        if fname.startswith("NC-SUPER-"):
            return "super_tools", "NC-SUPER"
        if fname.startswith("NC-MCP-"):
            return "mcp_core", "NC-MCP"
        if fname.startswith("NC-TOOL-"):
            return "tools", "NC-TOOL"
        return "tools", "NC-TOOL"
    if "/infra/llm/" in rel_path:
        return "llm_backends", "NC-LLM-FR"
    if "/infra/" in rel_path:
        return "infrastructure", "NC-INFRA-FR"
    if "/repositories/" in rel_path:
        return "repositories", "NC-REP-FR"
    if "/agent/" in rel_path:
        return "agents", "NC-AGENT-FR"
    if "/cli/" in rel_path:
        return "cli", "NC-CLI-FR"
    if "/mcp/" in rel_path:
        return "mcp", "NC-MCP-FR"
    if "/32-scripts/" in rel_path:
        return "scripts", "NC-SCR-FR"
    if "/33-tests/" in rel_path:
        return "tests", "NC-TEST-FR"
    if "/30-hooks/" in rel_path:
        return "hook_scripts", "NC-HK-FR"
    return "other", "NC-OTHER"


def extract_ncid(fname: str) -> str:
    m = re.match(r"^(NC-(?:[A-Z]+-){1,2}\d+)", fname)
    return m.group(1) if m else fname


def extract_desc(fname: str, ncid: str) -> str:
    rest = fname.removeprefix(ncid + "-")
    return rest.removesuffix(".py").removesuffix(".yaml").removesuffix(".json").removesuffix(".mdc")


def scan() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    entries = {"services": [], "tools": [], "engines": []}
    counts = {}

    for py_file in sorted(FW.rglob("*.py")):
        rel = str(py_file.relative_to(FW)).replace("\\", "/")
        fname = py_file.name

        # Skip pycache, archive, .neocortex
        if "__pycache__" in rel or "99-archive" in rel or ".neocortex" in rel:
            continue
        # Only NC- files
        if not fname.startswith("NC-"):
            continue

        cat, prefix = categorize(rel, fname)
        ncid = extract_ncid(fname)
        desc = extract_desc(fname, ncid)

        # Compute short hash
        try:
            h = hashlib.sha256(py_file.read_bytes()).hexdigest()[:12]
        except Exception:
            h = "?"

        entry = {
            "id": ncid,
            "name": fname,
            "desc": desc,
            "path": rel,
            "hash": h,
            "size": py_file.stat().st_size,
            "category": cat,
        }

        # Map to LEXICO's top-level categories
        if cat in ("engines", "llm_backends", "infrastructure", "utilities", "repositories"):
            entries["engines"].append(entry)
        elif cat in ("super_tools", "tools", "mcp_core", "mcp"):
            entries["tools"].append(entry)
        elif cat in ("services", "hooks", "agents", "cli"):
            entries["services"].append(entry)
        elif cat in ("scripts", "hook_scripts"):
            entries["scripts"] = entries.get("scripts", []) + [entry]
        else:
            entries["other"] = entries.get("other", []) + [entry]

        counts[cat] = counts.get(cat, 0) + 1

    return {
        "version": "4.6",
        "generated_at": ts,
        "source": "disk-scan-regenerated",
        "total_services": len(entries.get("services", [])),
        "total_tools": len(entries["tools"]),
        "total_engines": len(entries["engines"]),
        "total_scripts": len(entries.get("scripts", [])),
        "total_other": len(entries.get("other", [])),
        "total_files": sum(len(v) for v in entries.values() if isinstance(v, list)),
        "category_counts": counts,
        "services": entries.get("services", []),
        "tools": entries["tools"],
        "engines": entries["engines"],
        "scripts": entries.get("scripts", []),
        "other": entries.get("other", []),
    }


def main():
    data = scan()
    LEXICO_PATH.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(data, ensure_ascii=False, indent=2)
    LEXICO_PATH.write_text(json_text, encoding="utf-8")

    print(f"LEXICO v{data['version']} regenerated")
    print(f"  engines: {data['total_engines']}")
    print(f"  tools:   {data['total_tools']}")
    print(f"  services:{data['total_services']}")
    print(f"  other:   {data['total_other']}")
    print(f"\nCategories:")
    for cat, n in sorted(data["category_counts"].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
