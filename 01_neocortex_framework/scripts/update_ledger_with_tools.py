#!/usr/bin/env python3
"""
Update ledger with tools manifest reference.
"""

import json
from pathlib import Path

# Paths
LEDGER_PATH = (
    Path(__file__).parent
    / "DIR-CORE-FR-001-core-central"
    / "NC-LED-FR-001-framework-ledger.json"
)
MANIFEST_PATH = Path(__file__).parent / "neocortex" / "mcp" / "tools_manifest.json"


def main():
    print(f"Reading ledger from {LEDGER_PATH}")

    # Read ledger
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    # Add tools manifest reference
    if "mcp_tools" not in ledger:
        ledger["mcp_tools"] = {}

    ledger["mcp_tools"]["manifest_path"] = str(
        MANIFEST_PATH.relative_to(Path(__file__).parent)
    )
    ledger["mcp_tools"]["total_tools"] = 16
    ledger["mcp_tools"]["total_actions"] = 57
    ledger["mcp_tools"]["version"] = "4.2-cortex"

    # Also add a timestamp
    from datetime import datetime

    ledger["mcp_tools"]["last_updated"] = datetime.now().isoformat() + "Z"

    # Write back
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)

    print(f"Updated ledger with tools manifest reference")
    print(f"Manifest path: {ledger['mcp_tools']['manifest_path']}")


if __name__ == "__main__":
    main()
