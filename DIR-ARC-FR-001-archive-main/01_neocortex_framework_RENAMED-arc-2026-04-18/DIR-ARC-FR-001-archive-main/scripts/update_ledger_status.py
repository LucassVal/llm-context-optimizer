#!/usr/bin/env python3
"""
Update ledger status after PHASE 2 completion.
"""

import json
import datetime
import sys
import os

ledger_path = "neocortex_framework/DIR-CORE-FR-001-core-central/NC-LED-FR-001-framework-ledger.json"

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# Add status update event
new_event = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "event": "phase2_completed",
    "description": "PHASE 2 (Consolidacao + AKL) completed. Both neocortex_consolidation and neocortex_akl tools implemented and verified. MCP server operational with FastMCP.",
}

if "session_timeline" in ledger:
    ledger["session_timeline"].append(new_event)

# Update action_queue
if "action_queue" in ledger:
    # Move completed items
    completed_to_move = ["implement_consolidation_tool", "implement_akl_tool"]
    for item in completed_to_move:
        if item in ledger["action_queue"].get("in_progress", []):
            ledger["action_queue"]["in_progress"].remove(item)
            if "completed" in ledger["action_queue"]:
                ledger["action_queue"]["completed"].append(item)

    # Add new pending items for PHASE 3
    new_pending = [
        "implement_peers_tool",
        "implement_security_tool",
        "sanitize_root_directory",
        "update_white_label_docs",
    ]
    for item in new_pending:
        if item not in ledger["action_queue"].get("pending", []):
            ledger["action_queue"]["pending"].append(item)

    # Ensure implement_mcp_server is completed
    if "implement_mcp_server" in ledger["action_queue"].get("in_progress", []):
        ledger["action_queue"]["in_progress"].remove("implement_mcp_server")
        ledger["action_queue"]["completed"].append("implement_mcp_server")

# Update session metrics
if "session_metrics" in ledger:
    ledger["session_metrics"]["total_interactions"] = (
        ledger["session_metrics"].get("total_interactions", 0) + 1
    )

# Write back
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=2, ensure_ascii=False)

print("Ledger updated with PHASE 2 completion.")
