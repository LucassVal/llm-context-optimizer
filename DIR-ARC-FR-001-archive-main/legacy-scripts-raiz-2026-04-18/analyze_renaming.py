#!/usr/bin/env python3
import yaml
from datetime import datetime, timedelta
import json


def load_yaml(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def analyze_geographic_scope(plan):
    """Identify old_path that are not under neocortex/ or scripts/"""
    intrusos = []
    for entry in plan:
        old = entry.get("old_path", "")
        if not old.startswith("neocortex/") and not old.startswith("scripts/"):
            intrusos.append(old)
    return intrusos


def deduplicate_plan(plan):
    """Remove duplicate entries based on old_path"""
    seen = set()
    deduplicated = []
    for entry in plan:
        old = entry.get("old_path")
        if old not in seen:
            seen.add(old)
            deduplicated.append(entry)
    return deduplicated


def main():
    plan_path = r"01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2.yaml"
    catalog_path = r"DIR-DOC-FR-001-docs-main\artifact_catalog.json"

    print("Loading renaming plan...")
    data = load_yaml(plan_path)
    plan = data.get("renaming_plan", [])
    print(f"Total entries in plan: {len(plan)}")

    # Deduplicate
    dedup = deduplicate_plan(plan)
    print(f"Unique entries after deduplication: {len(dedup)}")

    # 1. Geographic scope analysis
    intrusos = analyze_geographic_scope(dedup)
    print("\n=== GEOGRAPHIC SCOPE ANALYSIS ===")
    print(f"Found {len(intrusos)} intrusive paths (not under neocortex/ or scripts/):")
    for path in intrusos:
        print(f"  - {path}")

    # 2. Recency analysis (requires catalog)
    print("\n=== RECENCY ANALYSIS ===")
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        print(f"Catalog loaded with {len(catalog)} entries")

        # Build mapping from relative path to modification date
        catalog_map = {}
        for item in catalog:
            rel_path = item.get("relative_path", "")
            mod_date_str = item.get("modified_date", "")
            if rel_path and mod_date_str:
                # Convert string to datetime
                try:
                    mod_date = datetime.fromisoformat(
                        mod_date_str.replace("Z", "+00:00")
                    )
                    catalog_map[rel_path] = mod_date
                except ValueError:
                    pass

        # Check each old_path in plan
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_files = []
        for entry in dedup:
            old = entry.get("old_path")
            # Prepend framework root to match catalog relative paths?
            # Catalog paths seem to be relative to project root, e.g., "01_neocortex_framework/neocortex/agent/executor.py"
            # Need to convert old_path to catalog key
            catalog_key = f"01_neocortex_framework/{old}"
            if catalog_key in catalog_map:
                mod_date = catalog_map[catalog_key]
                if mod_date > recent_cutoff:
                    recent_files.append((old, mod_date.isoformat()))

        print(f"Files modified in last 7 days: {len(recent_files)}")
        for path, date in recent_files:
            print(f"  - {path} ({date})")
    except Exception as e:
        print(f"Error loading catalog: {e}")

    # 3. Critical category validation (simplified)
    print("\n=== CRITICAL CATEGORY VALIDATION ===")
    critical_files = [
        "neocortex/config.py",
        "neocortex/mcp/server.py",
        "neocortex/mcp/sub_server.py",
        "neocortex/agent/executor.py",
        "neocortex/cli/main.py",
    ]
    for crit in critical_files:
        # Find entry
        entry = None
        for e in dedup:
            if e.get("old_path") == crit:
                entry = e
                break
        if entry:
            new = entry.get("new_path", "")
            # Infer category from new_path prefix
            if new.startswith("neocortex/NC-CORE"):
                inferred = "CORE"
            elif new.startswith("neocortex/mcp/NC-CORE"):
                inferred = "MCP"
            elif new.startswith("neocortex/agent/NC-AGENT"):
                inferred = "AGENT"
            elif new.startswith("neocortex/cli/NC-CLI"):
                inferred = "CLI"
            else:
                inferred = "OTHER"
            print(f"{crit} -> {new} (inferred category: {inferred})")
        else:
            print(f"{crit} NOT in renaming plan")

    # Output deduplicated plan summary
    print("\n=== DEDUPLICATED PLAN SUMMARY ===")
    print(f"Unique files to rename: {len(dedup)}")

    # Save deduplicated plan to YAML for later use
    output_plan = {"metadata": data.get("metadata", {}), "renaming_plan": dedup}
    output_path = (
        r"01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2_dedup.yaml"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(output_plan, f, default_flow_style=False, allow_unicode=True)
    print(f"Deduplicated plan saved to {output_path}")


if __name__ == "__main__":
    main()
