#!/usr/bin/env python3
"""
Update ledger and cortex with Antigravity MCP confirmation.
"""

import json
import datetime
import os

# Paths
ledger_path = "neocortex_framework/DIR-CORE-FR-001-core-central/NC-LED-FR-001-framework-ledger.json"
cortex_path = "neocortex_framework/DIR-CORE-FR-001-core-central/.agents/rules/NC-CTX-FR-001-cortex-central.mdc"

# 1. Update ledger
print("Updating ledger with Antigravity confirmation...")
with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# Add Antigravity confirmation event
antigravity_event = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "event": "antigravity_integration_confirmed",
    "description": "MCP server confirmed operational in Antigravity IDE. All 14 tools visible: neocortex_cortex, neocortex_lobes, neocortex_checkpoint, neocortex_regression, neocortex_ledger, neocortex_benchmark, neocortex_agent, neocortex_init, neocortex_config, neocortex_export, neocortex_manifest, neocortex_kg, neocortex_consolidation, neocortex_akl. Integration successful.",
}

if "session_timeline" in ledger:
    ledger["session_timeline"].append(antigravity_event)

# Update action_queue - mark implement_mcp_server as completed if still in progress
if "action_queue" in ledger:
    if "implement_mcp_server" in ledger["action_queue"].get("in_progress", []):
        ledger["action_queue"]["in_progress"].remove("implement_mcp_server")
        ledger["action_queue"]["completed"].append("implement_mcp_server")

    # Add review_mcp_compliance as completed
    if "review_mcp_compliance" in ledger["action_queue"].get("pending", []):
        ledger["action_queue"]["pending"].remove("review_mcp_compliance")
        ledger["action_queue"]["completed"].append("review_mcp_compliance")

# Update session metrics
if "session_metrics" in ledger:
    ledger["session_metrics"]["total_interactions"] = (
        ledger["session_metrics"].get("total_interactions", 0) + 1
    )

# Write back ledger
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=2, ensure_ascii=False)

print("[OK] Ledger updated")

# 2. Update cortex
print("\nUpdating cortex...")
with open(cortex_path, "r", encoding="utf-8") as f:
    cortex_content = f.read()

# Mark sanitization as completed
cortex_content = cortex_content.replace(
    "- [ ] Sanitize root directory structure",
    "- [x] Sanitize root directory structure ",
)

# Add MCP operational status note
# Find the Next Steps section and add a note
next_steps_marker = "- **Next Steps:**"
if next_steps_marker in cortex_content:
    # Insert a note after Next Steps
    insert_point = cortex_content.find(next_steps_marker) + len(next_steps_marker)
    new_note = "\n  - **MCP Status:** 14 tools operational in Antigravity "
    cortex_content = (
        cortex_content[:insert_point] + new_note + cortex_content[insert_point:]
    )

# Write back cortex
with open(cortex_path, "w", encoding="utf-8") as f:
    f.write(cortex_content)

print("[OK] Cortex updated")

print("\n=== Summary ===")
print(" Antigravity integration confirmed in ledger")
print(" MCP server marked as fully operational")
print(" Root sanitization marked as completed in cortex")
print(" 14 tools verified in Antigravity IDE")
