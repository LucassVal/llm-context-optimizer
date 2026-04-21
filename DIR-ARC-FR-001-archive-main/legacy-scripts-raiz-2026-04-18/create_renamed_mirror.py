#!/usr/bin/env python3
import shutil
import yaml
import re
from pathlib import Path


def load_dedup_plan():
    plan_path = (
        r"01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2_dedup.yaml"
    )
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("renaming_plan", [])


def normalize_path_sep(path):
    return path.replace("\\", "/")


def build_rename_map(plan):
    """Return dict old -> new (both normalized forward slashes)"""
    mapping = {}
    for entry in plan:
        old = normalize_path_sep(entry["old_path"])
        new = normalize_path_sep(entry["new_path"])
        mapping[old] = new
    return mapping


def should_skip(path):
    """Skip venv, __pycache__, .git, etc."""
    parts = Path(path).parts
    if any(part.startswith(".") for part in parts):
        return True
    if any(
        part in ("venv", "__pycache__", ".git", ".idea", ".vscode") for part in parts
    ):
        return True
    if path.endswith(".pyc"):
        return True
    return False


def copy_tree(src_root, dst_root, rename_map):
    """
    Copy entire src_root to dst_root, applying rename_map to files.
    Also update Python imports in renamed files.
    """
    src_root = Path(src_root)
    dst_root = Path(dst_root)

    # First pass: copy everything except skipped directories
    for src_path in src_root.rglob("*"):
        if should_skip(str(src_path)):
            continue
        rel_path = src_path.relative_to(src_root)
        rel_str = normalize_path_sep(str(rel_path))

        # Determine destination path (maybe renamed)
        dst_rel_str = rename_map.get(rel_str, rel_str)
        dst_path = dst_root / dst_rel_str

        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
            continue

        # Ensure parent directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {rel_str} -> {dst_rel_str}")

    # Second pass: update imports in renamed Python files
    for old_rel, new_rel in rename_map.items():
        dst_file = dst_root / new_rel
        if not dst_file.exists():
            print(f"Warning: renamed file not found at {dst_file}")
            continue
        if dst_file.suffix == ".py":
            update_imports_in_file(dst_file, rename_map)


def update_imports_in_file(file_path, rename_map):
    """Update import statements in a Python file based on rename mapping."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping non-text file: {file_path}")
        return

    # Build mapping from old module path to new module path
    # For each old path, compute the corresponding module path (without .py)
    module_map = {}
    for old, new in rename_map.items():
        if old.endswith(".py"):
            old_mod = old[:-3].replace("/", ".")
            new_mod = new[:-3].replace("/", ".")
            module_map[old_mod] = new_mod

    # Also map submodules (e.g., neocortex.core.file_utils -> neocortex.core.NC-CORE-FR-014-file-utils)
    # We'll do simple string replacement for each mapping
    updated = content
    for old_mod, new_mod in module_map.items():
        # Replace import statements
        # Pattern: import old_mod
        # Pattern: from old_mod import ...
        # Use regex to avoid replacing substrings inside strings
        pattern = r"(?m)^(\s*)(import|from)\s+" + re.escape(old_mod) + r"(\s|$)"

        def repl(match):
            indent = match.group(1)
            keyword = match.group(2)
            return f"{indent}{keyword} {new_mod}{match.group(3)}"

        updated = re.sub(pattern, repl, updated)

        # Also handle relative imports? Might be tricky; skip for now.

    if updated != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"Updated imports in: {file_path.relative_to(file_path.parent.parent)}")


def main():
    src = r"01_neocortex_framework"
    dst = r"01_neocortex_framework_RENAMED"

    print(f"Source: {src}")
    print(f"Destination: {dst}")

    plan = load_dedup_plan()
    print(f"Loaded {len(plan)} rename mappings")

    rename_map = build_rename_map(plan)
    print("Rename mapping preview (first 5):")
    for i, (old, new) in enumerate(list(rename_map.items())[:5]):
        print(f"  {old} -> {new}")

    # Ensure destination is empty
    dst_path = Path(dst)
    if dst_path.exists():
        print("Destination exists, removing...")
        shutil.rmtree(dst_path)
    dst_path.mkdir(parents=True)

    copy_tree(src, dst_path, rename_map)

    # Generate statistics
    total_files = sum(1 for _ in dst_path.rglob("*") if _.is_file())
    renamed_files = len(rename_map)
    print("\nMirror creation complete.")
    print(f"Total files copied: {total_files}")
    print(f"Files renamed: {renamed_files}")

    # Save copy of rename mapping for reference
    mapping_file = dst_path / "RENAME_MAPPING.yaml"
    with open(mapping_file, "w", encoding="utf-8") as f:
        yaml.dump(
            {"rename_mapping": [{"old": k, "new": v} for k, v in rename_map.items()]}, f
        )
    print(f"Mapping saved to {mapping_file}")


if __name__ == "__main__":
    main()
