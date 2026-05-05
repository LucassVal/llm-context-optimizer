# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.554105'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
---"""

"""
Approve handoffs: update status PENDING_REVIEW  APPROVED in audit-logs
and update queue YAML to DONE for approved tickets.
Usage: python approve_handoffs.py NC-DS-014 NC-DS-027
"""
import re
import sys
from datetime import datetime
from pathlib import Path

base = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
audit = base / "DIR-DS-002-audit-logs"
queue_path = base / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"

tickets_to_approve = sys.argv[1:] if len(sys.argv) > 1 else ["NC-DS-014", "NC-DS-027"]
now = datetime.now().isoformat(timespec="seconds")

approved = []
for tid in tickets_to_approve:
    # Find handoff files
    handoffs = sorted(audit.glob(f"{tid}-handoff-*.yaml"))
    if not handoffs:
        print(f"  {tid}: SEM HANDOFF")
        continue
    hf = handoffs[-1]  # most recent
    c = hf.read_text(encoding="utf-8")
    if "PENDING_REVIEW" in c:
        c = c.replace("status: PENDING_REVIEW", "status: APPROVED", 1)
        c += f"\napproved_at: \"{now}\"\napproved_by: antigravity-t0\n"
        hf.write_text(c, encoding="utf-8")
        approved.append(tid)
        print(f"   {tid}: APPROVED ({hf.name})")
    elif "APPROVED" in c:
        print(f"    {tid}: j APPROVED")
    else:
        print(f"    {tid}: status inesperado")

# Update queue: set approved tickets to DONE
q = queue_path.read_text(encoding="utf-8")
for tid in approved:
    # Find the ticket block and update status
    pattern = rf'(ticket_id: {re.escape(tid)}.*?status:)\s*(ACTIVE|CLAIMED|AVAILABLE|BLOCKED)'
    m = re.search(pattern, q, re.DOTALL)
    if m:
        q = q[:m.start(2)] + "DONE" + q[m.end(2):]
        q = q.replace(m.group(0), m.group(1) + " DONE", 1)
        print(f"   Fila: {tid}  DONE")

# Simpler approach for queue update
q2 = queue_path.read_text(encoding="utf-8")
lines = q2.splitlines(keepends=True)
new_lines = []
current = None
for line in lines:
    m = re.search(r'ticket_id: (NC-DS-\d+)', line)
    if m:
        current = m.group(1)
    if current in approved and '    status: ' in line and 'DONE' not in line:
        old_status = re.search(r'    status: (\w+)', line)
        if old_status and old_status.group(1) in ('ACTIVE', 'CLAIMED', 'AVAILABLE', 'BLOCKED', 'PENDING_REVIEW'):
            line = line.replace(f'    status: {old_status.group(1)}', '    status: DONE')
            print(f"   Queue {current}: {old_status.group(1)}  DONE")
    new_lines.append(line)
queue_path.write_text("".join(new_lines), encoding="utf-8")

# Final count
q3 = queue_path.read_text(encoding="utf-8")
avail  = len(re.findall(r'    status: AVAILABLE', q3))
done   = len(re.findall(r'    status: DONE', q3))
active = len(re.findall(r'    status: ACTIVE', q3))
print(f"\nFila: AVAILABLE={avail} DONE={done} ACTIVE={active}")
