#!/usr/bin/env python3
"""
Add MCP verification event to ledger.
"""

import json
import datetime
import sys

ledger_path = "NC-LED-FR-001-framework-ledger.json"

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# Add new event to timeline
new_event = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "event": "mcp_verification",
    "description": "Verified MCP server with FastMCP installed. 14 tools registered including neocortex_manifest, neocortex_kg, neocortex_consolidation, neocortex_akl. Core functions operational.",
}

# Insert before the last event (session_end) or append
if "session_timeline" in ledger:
    ledger["session_timeline"].append(new_event)

    # Update total_interactions
    if (
        "session_metrics" in ledger
        and "total_interactions" in ledger["session_metrics"]
    ):
        ledger["session_metrics"]["total_interactions"] += 1

# Write back
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=2, ensure_ascii=False)

print("Ledger updated with MCP verification event.")
