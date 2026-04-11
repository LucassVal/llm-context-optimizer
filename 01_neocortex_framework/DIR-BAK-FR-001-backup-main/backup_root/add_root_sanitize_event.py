#!/usr/bin/env python3
"""
Add root sanitization event to ledger.
"""

import json
import datetime

ledger_path = "neocortex_framework/DIR-CORE-FR-001-core-central/NC-LED-FR-001-framework-ledger.json"

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# Add sanitization event
new_event = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "event": "root_sanitization",
    "description": "Sanitized root directory: moved unnecessary files to backup_root, kept only white_label, neocortex_framework, examples, .agents, and essential documentation. Templates moved to framework templates directory.",
}

if "session_timeline" in ledger:
    ledger["session_timeline"].append(new_event)

# Update action_queue
if "action_queue" in ledger:
    # Add sanitization as completed
    if "sanitize_root_directory" in ledger["action_queue"].get("pending", []):
        ledger["action_queue"]["pending"].remove("sanitize_root_directory")
        ledger["action_queue"]["completed"].append("sanitize_root_directory")

# Write back
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=2, ensure_ascii=False)

print("Ledger updated with root sanitization event.")
