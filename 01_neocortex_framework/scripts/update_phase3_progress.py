#!/usr/bin/env python3
"""
Update ledger and cortex with PHASE 3 progress.
"""

import json
import datetime

# Paths
ledger_path = "neocortex_framework/DIR-CORE-FR-001-core-central/NC-LED-FR-001-framework-ledger.json"
cortex_path = "neocortex_framework/DIR-CORE-FR-001-core-central/.agents/rules/NC-CTX-FR-001-cortex-central.mdc"

print("Updating ledger with PHASE 3 implementation...")

# 1. Update ledger
with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# Add PHASE 3 implementation event
phase3_event = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "event": "phase3_peers_security_implemented",
    "description": "PHASE 3 (Peers + Security) tools implemented: neocortex_peers (3 actions: discover, sync_state, resolve_conflict) and neocortex_security (3 actions: validate_access, audit_changes, encrypt_sensitive). All 16 MCP tools now implemented.",
}

if "session_timeline" in ledger:
    ledger["session_timeline"].append(phase3_event)

# Update action_queue
if "action_queue" in ledger:
    # Remove from pending, add to completed
    pending_to_complete = [
        "implement_peers_tool",
        "implement_security_tool",
        "implement_peers_security",
    ]
    for item in pending_to_complete:
        if item in ledger["action_queue"].get("pending", []):
            ledger["action_queue"]["pending"].remove(item)
            ledger["action_queue"]["completed"].append(item)

    # Add complete_phase3 to completed
    if "complete_phase3" not in ledger["action_queue"]["completed"]:
        ledger["action_queue"]["completed"].append("complete_phase3")

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

# Mark PHASE 3 items as completed
cortex_content = cortex_content.replace(
    "- [ ] Implement neocortex_peers tool (3 actions)",
    "- [x] Implement neocortex_peers tool (3 actions) ",
)

cortex_content = cortex_content.replace(
    "- [ ] Implement neocortex_security tool (3 actions)",
    "- [x] Implement neocortex_security tool (3 actions) ",
)

cortex_content = cortex_content.replace(
    "- [ ] Complete PHASE 3 (Peers + Security)",
    "- [x] Complete PHASE 3 (Peers + Security) ",
)

# Update Next Steps section - add completion note
if "**Next Steps:**" in cortex_content:
    # Add achievement note
    achievement_note = (
        "\n  - **PHASE 3 COMPLETE**: All 16 MCP tools implemented (100%) "
    )
    cortex_content = cortex_content.replace(
        "**Next Steps:**", "**Next Steps:**" + achievement_note
    )

# Write back cortex
with open(cortex_path, "w", encoding="utf-8") as f:
    f.write(cortex_content)

print("[OK] Cortex updated")

# 3. Update Claude assistant lobe
claude_path = "neocortex_framework/DIR-CORE-FR-001-core-central/.agents/rules/NC-LBE-FR-002-claude-assistant.mdc"
print("\nUpdating Claude assistant lobe...")

with open(claude_path, "r", encoding="utf-8") as f:
    claude_content = f.read()

# Mark CP-CLA-011 and CP-CLA-012 as completed
claude_content = claude_content.replace(
    "- [ ] **CP-CLA-011**  Implement `neocortex_peers` (3 actions)",
    "- [x] **CP-CLA-011**  Implement `neocortex_peers` (3 actions) ",
)

claude_content = claude_content.replace(
    "- [ ] **CP-CLA-012**  Implement `neocortex_security` (3 actions)",
    "- [x] **CP-CLA-012**  Implement `neocortex_security` (3 actions) ",
)

# Update progress metrics
claude_content = claude_content.replace(
    "- **Current Tools**: 14 (88%)", "- **Current Tools**: 16 (100%)"
)

claude_content = claude_content.replace(
    "- **Current Actions**: 48 (59%)",
    "- **Current Actions**: 54 (67%)",  # 48 + 6 new actions = 54
)

claude_content = claude_content.replace(
    "- **Remaining Actions**: 33",
    "- **Remaining Actions**: 27",  # 81 - 54 = 27
)

# Update Current Focus section
new_focus = """##  Current Focus (POST-PHASE 3  Integration & Polish)
**Immediate Next Actions:**
1. **Test all 16 MCP tools**  Verify functionality in simulation mode
2. **Update white label documentation**  Complete template documentation
3. **Run benchmark integration**  Ensure performance metrics
4. **Create final validation suite**  End-to-end testing

**Expected Output:**
- All 16 tools functional and verified
- White label template fully documented
- Benchmark results updated
- Framework ready for production use"""

if "##  Current Focus (PHASE 3  Peers + Security)" in claude_content:
    claude_content = claude_content.replace(
        "##  Current Focus (PHASE 3  Peers + Security)", new_focus
    )

# Write back claude lobe
with open(claude_path, "w", encoding="utf-8") as f:
    f.write(claude_content)

print("[OK] Claude assistant lobe updated")

print("\n=== PHASE 3 IMPLEMENTATION COMPLETE ===")
print(" neocortex_peers tool implemented (3 actions)")
print(" neocortex_security tool implemented (3 actions)")
print(" All 16 MCP tools now implemented (100%)")
print(" 54/81 actions implemented (67%)")
print(" Ledger, cortex, and claude lobe updated")
