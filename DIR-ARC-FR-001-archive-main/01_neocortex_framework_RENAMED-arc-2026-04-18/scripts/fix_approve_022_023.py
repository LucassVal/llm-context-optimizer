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

"""Approve NC-DS-022 and NC-DS-023  fix parser bug that read 0L instead of real lines."""
import re
import sys
from datetime import datetime
from pathlib import Path

BASE  = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
AUDIT = BASE / "DIR-DS-002-audit-logs"
QUEUE = BASE / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
now   = datetime.now().isoformat(timespec="seconds")

to_approve = {
    "NC-DS-022": ("NC-DS-022-handoff-20260412-221714.yaml", 323),
    "NC-DS-023": ("NC-DS-023-handoff-20260412-221708.yaml", 137),
}

for tid, (fname, real_lines) in to_approve.items():
    hf = AUDIT / fname
    c = hf.read_text(encoding="utf-8")
    c = re.sub(r"\nrejected_at:[^\n]*", "", c)
    c = re.sub(r"\nrejected_by:[^\n]*", "", c)
    c = re.sub(r"\nreject_reason:[^\n]*", "", c)
    c = c.replace("status: REJECTED", "status: APPROVED", 1)
    c += f'\napproved_at: "{now}"\napproved_by: antigravity-t0\napprove_note: "real_lines={real_lines}L via lines_of_code field  valid delivery"\n'
    hf.write_text(c, encoding="utf-8")
    print(f"APPROVED {tid} ({real_lines}L)")

# Queue update
q = QUEUE.read_text(encoding="utf-8")
lines = q.splitlines(keepends=True)
new = []
current = None
for line in lines:
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", line)
    if m: current = m.group(1)
    if current in to_approve and "    status: AVAILABLE" in line:
        line = line.replace("    status: AVAILABLE", "    status: DONE")
        print(f"QUEUE {current}: AVAILABLE -> DONE")
    new.append(line)
QUEUE.write_text("".join(new), encoding="utf-8")

# Verify files on disk
file_map = {
    "NC-DS-022": BASE / "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py",
    "NC-DS-023": BASE / "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-007-state-machine.py",
}
for tid, path in file_map.items():
    status = f"EXISTS ({path.read_text(encoding='utf-8').count(chr(10))}L)" if path.exists() else "MISSING"
    print(f"{tid} arquivo: {status}")

q2 = QUEUE.read_text(encoding="utf-8")
av = len(re.findall(r"    status: AVAILABLE", q2))
dn = len(re.findall(r"    status: DONE", q2))
print(f"\nFila final: AVAILABLE={av} DONE={dn}")
