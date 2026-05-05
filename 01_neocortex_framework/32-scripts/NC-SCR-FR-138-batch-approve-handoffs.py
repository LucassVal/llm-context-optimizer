# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.563030'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  -
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.563030'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  -
---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.563030'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
---"""

"""Batch approve/reject PENDING_REVIEW handoffs based on lines_added threshold."""
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
AUDIT = BASE / "DIR-DS-002-audit-logs"
QUEUE = BASE / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
now = datetime.now().isoformat(timespec="seconds")

approved = set()
rejected = set()

# Find best handoff per ticket (highest lines_added among PENDING_REVIEW)
best = {}
for hf in sorted(AUDIT.glob("NC-DS-*-handoff-*.yaml")):
    c = hf.read_text(encoding="utf-8")
    if "PENDING_REVIEW" not in c:
        continue
    m_tid = re.search(r"ticket_id:\s*(NC-DS-\d+)", c)
    m_la  = re.search(r"lines_added:\s*(\d+)", c)
    if not m_tid:
        continue
    tid = m_tid.group(1)
    la  = int(m_la.group(1)) if m_la else 0
    if tid not in best or la > best[tid][1]:
        best[tid] = (hf, la)

for tid, (hf, la) in sorted(best.items()):
    c = hf.read_text(encoding="utf-8")
    if la >= 50:
        c = c.replace("status: PENDING_REVIEW", "status: APPROVED", 1)
        c += f'\napproved_at: "{now}"\napproved_by: antigravity-t0\n'
        hf.write_text(c, encoding="utf-8")
        approved.add(tid)
        print(f"  APPROVED {tid} ({la}L) {hf.name}")
    elif la < 10:
        c = c.replace("status: PENDING_REVIEW", "status: REJECTED", 1)
        c += f'\nrejected_at: "{now}"\nrejected_by: antigravity-t0\nreject_reason: "lines_added={la} below threshold=10"\n'
        hf.write_text(c, encoding="utf-8")
        rejected.add(tid)
        print(f"  REJECTED {tid} ({la}L) insufficient delivery")
    else:
        print(f"  MANUAL  {tid} ({la}L) needs T0 review")

# Reject remaining duplicate PENDING_REVIEW for already-approved tickets
for hf in AUDIT.glob("NC-DS-*-handoff-*.yaml"):
    c = hf.read_text(encoding="utf-8")
    if "PENDING_REVIEW" not in c:
        continue
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", c)
    if not m:
        continue
    tid = m.group(1)
    if tid in approved or tid in rejected:
        m_la = re.search(r"lines_added:\s*(\d+)", c)
        la = int(m_la.group(1)) if m_la else 0
        c = c.replace("status: PENDING_REVIEW", "status: REJECTED", 1)
        c += f'\nrejected_at: "{now}"\nrejected_by: antigravity-t0\nreject_reason: "duplicate handoff, best already processed ({la}L)"\n'
        hf.write_text(c, encoding="utf-8")
        print(f"  REJECTED DUP {tid} ({la}L) {hf.name}")

# Update queue
q = QUEUE.read_text(encoding="utf-8")
lines = q.splitlines(keepends=True)
new_lines = []
current = None
for line in lines:
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", line)
    if m:
        current = m.group(1)
    if current in approved and "    status: " in line:
        s = re.search(r"    status: (\w+)", line)
        if s and s.group(1) != "DONE":
            line = line.replace(f"    status: {s.group(1)}", "    status: DONE")
            print(f"  QUEUE {current}: {s.group(1)} -> DONE")
    if current in rejected and "    status: " in line:
        s = re.search(r"    status: (\w+)", line)
        if s and s.group(1) not in ("AVAILABLE", "DONE"):
            line = line.replace(f"    status: {s.group(1)}", "    status: AVAILABLE")
QUEUE.write_text("".join(new_lines if new_lines else lines), encoding="utf-8")

# Write fixed queue
QUEUE.write_text("".join(new_lines if new_lines else lines), encoding="utf-8")

# Re-read for stats
q2 = QUEUE.read_text(encoding="utf-8")
av = len(re.findall(r"    status: AVAILABLE", q2))
dn = len(re.findall(r"    status: DONE", q2))
ac = len(re.findall(r"    status: ACTIVE", q2))
print(f"\nFila final: AVAILABLE={av} DONE={dn} ACTIVE={ac}")
print(f"Approved: {sorted(approved)}")
print(f"Rejected: {sorted(rejected)}")
