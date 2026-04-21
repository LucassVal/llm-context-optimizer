#!/usr/bin/env python3
import yaml
import json
from datetime import datetime, timedelta


def load_yaml(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_catalog(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_path(path):
    """Normalize path separators to forward slashes and remove leading ./"""
    path = path.replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path


def deduplicate_plan(plan):
    seen = set()
    dedup = []
    for entry in plan:
        old = entry.get("old_path")
        if old not in seen:
            seen.add(old)
            dedup.append(entry)
    return dedup


def analyze_geographic_scope(plan):
    intrusos = []
    for entry in plan:
        old = entry.get("old_path", "")
        if not old.startswith("neocortex/") and not old.startswith("scripts/"):
            intrusos.append(old)
    return intrusos


def analyze_recency(plan, catalog):
    # Build mapping from normalized path to modified datetime
    path_to_date = {}

    # Process python_files
    for item in catalog.get("python_files", []):
        raw_path = item.get("path", "")
        if not raw_path:
            continue
        norm_path = normalize_path(raw_path)
        mod_str = item.get("modified", "")
        if mod_str:
            try:
                # Remove trailing Z and convert
                if mod_str.endswith("Z"):
                    mod_str = mod_str[:-1] + "+00:00"
                mod_dt = datetime.fromisoformat(mod_str)
                path_to_date[norm_path] = mod_dt
            except ValueError:
                pass

    # Process yaml_files (if needed)
    for item in catalog.get("yaml_files", []):
        raw_path = item.get("path", "")
        if not raw_path:
            continue
        norm_path = normalize_path(raw_path)
        mod_str = item.get("modified", "")
        if mod_str:
            try:
                if mod_str.endswith("Z"):
                    mod_str = mod_str[:-1] + "+00:00"
                mod_dt = datetime.fromisoformat(mod_str)
                path_to_date[norm_path] = mod_dt
            except ValueError:
                pass

    recent_cutoff = datetime.now() - timedelta(days=7)
    recent_files = []

    for entry in plan:
        old = entry.get("old_path")
        # Try to match with catalog path
        # Catalog paths are relative to base_dir, which is project root
        # old_path is relative to framework root? Actually old_path is like "neocortex/agent/executor.py"
        # Need to prepend "01_neocortex_framework/"
        candidate = f"01_neocortex_framework/{old}"
        candidate_norm = normalize_path(candidate)

        if candidate_norm in path_to_date:
            mod_dt = path_to_date[candidate_norm]
            if mod_dt > recent_cutoff:
                recent_files.append(
                    {
                        "old_path": old,
                        "modified": mod_dt.isoformat(),
                        "days_ago": (datetime.now() - mod_dt).days,
                    }
                )
        else:
            # Try without prefix
            if normalize_path(old) in path_to_date:
                mod_dt = path_to_date[normalize_path(old)]
                if mod_dt > recent_cutoff:
                    recent_files.append(
                        {
                            "old_path": old,
                            "modified": mod_dt.isoformat(),
                            "days_ago": (datetime.now() - mod_dt).days,
                        }
                    )

    return recent_files


def analyze_critical_categories(plan):
    critical = [
        ("neocortex/config.py", "CORE"),
        ("neocortex/mcp/server.py", "MCP"),
        ("neocortex/mcp/sub_server.py", "MCP"),
        ("neocortex/agent/executor.py", "AGENT"),
        ("neocortex/cli/main.py", "CLI"),
    ]
    results = []
    for old_path, expected_category in critical:
        entry = next((e for e in plan if e.get("old_path") == old_path), None)
        if entry:
            new_path = entry.get("new_path", "")
            # Infer category from new_path prefix
            inferred = "OTHER"
            if new_path.startswith("neocortex/NC-CORE"):
                inferred = "CORE"
            elif new_path.startswith("neocortex/mcp/NC-CORE"):
                inferred = "MCP"
            elif new_path.startswith("neocortex/agent/NC-AGENT"):
                inferred = "AGENT"
            elif new_path.startswith("neocortex/cli/NC-CLI"):
                inferred = "CLI"
            elif new_path.startswith("neocortex/infra/NC-INFRA"):
                inferred = "INFRA"
            elif new_path.startswith("neocortex/core/NC-CORE"):
                inferred = "CORE"
            elif new_path.startswith("neocortex/mcp/tools/NC-TOOL"):
                inferred = "TOOL"
            elif new_path.startswith("neocortex/repositories/NC-REPO"):
                inferred = "REPO"
            elif new_path.startswith("neocortex/schemas/NC-SCHEMA"):
                inferred = "SCHEMA"

            match = inferred == expected_category
            results.append(
                {
                    "old_path": old_path,
                    "new_path": new_path,
                    "expected_category": expected_category,
                    "inferred_category": inferred,
                    "match": match,
                }
            )
        else:
            results.append({"old_path": old_path, "error": "Not in renaming plan"})
    return results


def main():
    plan_path = r"01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2.yaml"
    catalog_path = r"DIR-DOC-FR-001-docs-main\artifact_catalog.json"

    print("Loading renaming plan...")
    data = load_yaml(plan_path)
    plan = data.get("renaming_plan", [])
    print(f"Total entries in plan: {len(plan)}")

    dedup = deduplicate_plan(plan)
    print(f"Unique entries after deduplication: {len(dedup)}")

    # 1. Geographic scope
    intrusos = analyze_geographic_scope(dedup)

    # 2. Recency analysis
    print("\nLoading catalog...")
    catalog = load_catalog(catalog_path)
    print(
        f"Catalog contains {len(catalog.get('python_files', []))} Python files and {len(catalog.get('yaml_files', []))} YAML files"
    )
    recent_files = analyze_recency(dedup, catalog)

    # 3. Critical category validation
    critical_results = analyze_critical_categories(dedup)

    # Prepare summary report
    summary = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "original_plan_entries": len(plan),
            "deduplicated_entries": len(dedup),
            "geographic_scope_intrusos_count": len(intrusos),
            "recent_files_count": len(recent_files),
        },
        "geographic_scope_intrusos": intrusos,
        "recent_files": recent_files,
        "critical_category_validation": critical_results,
        "deduplicated_plan": dedup,
    }

    # Save summary as YAML
    output_yaml = r"01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_analysis_summary.yaml"
    with open(output_yaml, "w", encoding="utf-8") as f:
        yaml.dump(summary, f, default_flow_style=False, allow_unicode=True)
    print(f"\nAnalysis summary saved to {output_yaml}")

    # Print human-readable report
    print("\n" + "=" * 60)
    print("RENAMING PLAN ANALYSIS REPORT")
    print("=" * 60)
    print("\n1. GEOGRAPHIC SCOPE ANALYSIS")
    print(f"   Intrusive paths (not under neocortex/ or scripts/): {len(intrusos)}")
    for path in intrusos:
        print(f"      - {path}")

    print("\n2. RECENCY ANALYSIS (last 7 days)")
    print(f"   Recently modified files: {len(recent_files)}")
    for item in recent_files:
        print(f"      - {item['old_path']} (modified {item['days_ago']} days ago)")

    print("\n3. CRITICAL CATEGORY VALIDATION")
    matches = sum(1 for r in critical_results if "match" in r and r["match"])
    total = len([r for r in critical_results if "match" in r])
    print(f"   Categories matched: {matches}/{total}")
    for r in critical_results:
        if "error" in r:
            print(f"      - {r['old_path']}: {r['error']}")
        else:
            status = "" if r["match"] else ""
            print(f"      - {status} {r['old_path']} -> {r['new_path']}")
            print(
                f"          expected: {r['expected_category']}, inferred: {r['inferred_category']}"
            )

    print("\n4. DEDUPLICATED PLAN")
    print(f"   Unique files to rename: {len(dedup)}")

    # Decision
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    if len(intrusos) == 0 and len(recent_files) == 0:
        print(" PLAN APPROVED. No intrusive paths and no recently modified files.")
        print("   Proceed with creating mirrored renamed copy.")
    else:
        print("  PLAN REQUIRES REVIEW.")
        if len(intrusos) > 0:
            print("   - Found intrusive paths (outside neocortex/ or scripts/).")
        if len(recent_files) > 0:
            print("   - Found recently modified files (may need manual review).")
        print("   Please review above findings before proceeding.")


if __name__ == "__main__":
    main()
