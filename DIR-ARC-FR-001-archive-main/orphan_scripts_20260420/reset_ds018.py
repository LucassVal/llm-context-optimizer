# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.801257'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
---"""

"""Reset NC-DS-018 to AVAILABLE and reject its insufficient handoff."""
import re
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
QUEUE = BASE / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
now = datetime.now().isoformat(timespec="seconds")

# Reset NC-DS-018 in queue
q = QUEUE.read_text(encoding="utf-8")
lines = q.splitlines(keepends=True)
new = []
current = None
for line in lines:
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", line)
    if m:
        current = m.group(1)
    if current == "NC-DS-018":
        if "    status: " in line:
            s = re.search(r"    status: (\w+)", line)
            if s and s.group(1) != "AVAILABLE":
                print(f"NC-DS-018: {s.group(1)} -> AVAILABLE")
                line = line.replace(f"    status: {s.group(1)}", "    status: AVAILABLE")
        elif "    claimed_by:" in line and "null" not in line:
            line = re.sub(r'    claimed_by:\s*".+"', "    claimed_by: null", line)
        elif "    completed_at:" in line and "null" not in line:
            line = re.sub(r'    completed_at:\s*".+"', "    completed_at: null", line)
    new.append(line)
QUEUE.write_text("".join(new), encoding="utf-8")
print("NC-DS-018 reset to AVAILABLE")

# Reject insufficient handoff
for hf in (BASE / "DIR-DS-002-audit-logs").glob("NC-DS-018-handoff-*.yaml"):
    c = hf.read_text(encoding="utf-8")
    if "PENDING_REVIEW" in c:
        c = c.replace("status: PENDING_REVIEW", "status: REJECTED", 1)
        c += f'\nrejected_at: "{now}"\nrejected_by: antigravity-t0\nreject_reason: "lines_added=15 below threshold=50. Reexecute full task."\n'
        hf.write_text(c, encoding="utf-8")
        print(f"Handoff rejected: {hf.name}")

# Final queue stats
q2 = QUEUE.read_text(encoding="utf-8")
av = len(re.findall(r"    status: AVAILABLE", q2))
dn = len(re.findall(r"    status: DONE", q2))
ac = len(re.findall(r"    status: ACTIVE", q2))
bl = len(re.findall(r"    status: BLOCKED", q2))
print(f"\nFila final: AVAILABLE={av} DONE={dn} ACTIVE={ac} BLOCKED={bl}")

# Also show which tickets are AVAILABLE
for m in re.finditer(r"ticket_id:\s*(NC-DS-\d+).*?status: AVAILABLE", q2, re.DOTALL):
    print(f"  AVAILABLE: {m.group(1)}")
