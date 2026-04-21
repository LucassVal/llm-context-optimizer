# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---"""

"""
Fix tickets: remove NC-NAM from exit_state.files_modified + reset queue BLOCKED/CLAIMEDAVAILABLE.
"""
import re
import sys
from pathlib import Path

base = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
ticket_dir = base / "DIR-DS-001-tickets"
queue_path = base / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"

LOCK_PATTERNS = [
    "NC-NAM-FR-001-naming-convention.md",
    "NC-TODO-FR-001-project-roadmap-consolidated.md",  # roadmap  workers no devem tocar
]

# 1. Fix tickets  remover linhas que referenciam @LOCKS em files_modified
fixed = 0
for f in sorted(ticket_dir.glob("NC-DS-0*.yaml")):
    content = f.read_text(encoding="utf-8")
    original = content
    lines = content.splitlines(keepends=True)
    new_lines = []
    in_modified = False
    for line in lines:
        if "files_modified:" in line:
            in_modified = True
        elif re.match(r"\S", line) and ":" in line and not line.strip().startswith("-"):
            in_modified = False
        # Skip lines that reference @LOCK files inside files_modified
        if in_modified and any(p in line for p in LOCK_PATTERNS):
            print(f"REMOVED from {f.name}: {line.strip()}")
            continue
        new_lines.append(line)
    new_content = "".join(new_lines)
    if new_content != original:
        f.write_text(new_content, encoding="utf-8")
        fixed += 1
print(f"Fixed {fixed} tickets")
print()

# 2. Reset queue: BLOCKED/CLAIMED  AVAILABLE (except NC-DS-020 which is DONE)
# NC-DS-020 is confirmed done, keep as DONE
# NC-DS-011/012/013/014 - legacy per-frente, keep DONE/ACTIVE
q = queue_path.read_text(encoding="utf-8")

# Track NC-DS-020 area to protect it
lines = q.splitlines(keepends=True)
new_lines = []
current_ticket = None
protect_done = {"NC-DS-020"}  # confirmed real deliveries
protect_active = {"NC-DS-014"}

i = 0
while i < len(lines):
    line = lines[i]
    m = re.search(r"ticket_id: (NC-DS-\d+)", line)
    if m:
        current_ticket = m.group(1)

    # Reset BLOCKED and errant CLAIMED to AVAILABLE
    if "    status: BLOCKED" in line and current_ticket not in protect_done:
        print(f"RESET {current_ticket}: BLOCKED  AVAILABLE")
        line = line.replace("status: BLOCKED", "status: AVAILABLE")
    elif "    status: CLAIMED" in line and current_ticket not in protect_done and current_ticket not in protect_active:
        print(f"RESET {current_ticket}: CLAIMED  AVAILABLE")
        line = line.replace("status: CLAIMED", "status: AVAILABLE")
        # Also clear claimed_by and claimed_at
    elif "    status: DONE" in line and current_ticket and current_ticket.startswith("NC-DS-0") and current_ticket not in protect_done:
        # Check if this is a "false DONE" (tasks 016-029 that didn't actually deliver)
        tnum = int(re.search(r"NC-DS-0(\d+)", current_ticket).group(1))
        if tnum >= 16 and current_ticket not in protect_done:
            print(f"RESET {current_ticket}: false DONE  AVAILABLE")
            line = line.replace("status: DONE", "status: AVAILABLE")

    new_lines.append(line)
    i += 1

queue_path.write_text("".join(new_lines), encoding="utf-8")

# Count final status
q2 = queue_path.read_text(encoding="utf-8")
avail  = len(re.findall(r"    status: AVAILABLE", q2))
done   = len(re.findall(r"    status: DONE", q2))
active = len(re.findall(r"    status: ACTIVE", q2))
claimed= len(re.findall(r"    status: CLAIMED", q2))
print(f"\nFila final: AVAILABLE={avail} DONE={done} ACTIVE={active} CLAIMED={claimed}")
