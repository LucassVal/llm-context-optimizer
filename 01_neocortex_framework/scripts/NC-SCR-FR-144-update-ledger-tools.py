#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.828640'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-LED-FR-001-framework-ledger
related_ssot:
  - NC-TLM-FR-001-tool-manifest
tags:
  - neocortex-other
  - level-0
  - python
---"""

"""
Update ledger with tools manifest reference.
"""

import json
import sys
from pathlib import Path

# Paths
LEDGER_PATH = (
    Path(__file__).parent
    / "DIR-CORE-FR-001-core-central"
    / "NC-LED-FR-001-framework-ledger.json"
)
MANIFEST_PATH = (
    Path(__file__).parent
    / "DIR-CORE-FR-001-core-central"
    / "NC-TLM-FR-001-tool-manifest.json"
)


def main():
    print(f"Reading ledger from {LEDGER_PATH}")

    # Read ledger
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    # Add tools manifest reference
    if "mcp_tools" not in ledger:
        ledger["mcp_tools"] = {}

    # Read manifest to get accurate counts
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        total_tools = len(manifest.get("tools", []))
        total_actions = sum(
            len(tool.get("actions", [])) for tool in manifest.get("tools", [])
        )
        version = manifest.get("version", "1.0.0")
    except Exception as e:
        print(f"Warning: Could not read manifest for counts: {e}")
        total_tools = 16
        total_actions = 57
        version = "4.2-cortex"

    ledger["mcp_tools"]["manifest_path"] = str(
        MANIFEST_PATH.relative_to(Path(__file__).parent)
    )
    ledger["mcp_tools"]["total_tools"] = total_tools
    ledger["mcp_tools"]["total_actions"] = total_actions
    ledger["mcp_tools"]["version"] = version

    # Also add a timestamp
    from datetime import datetime

    ledger["mcp_tools"]["last_updated"] = datetime.now().isoformat() + "Z"

    # Write back
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)

    print("Updated ledger with tools manifest reference")
    print(f"Manifest path: {ledger['mcp_tools']['manifest_path']}")


if __name__ == "__main__":
    main()
