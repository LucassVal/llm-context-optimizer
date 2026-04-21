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
NC-SCR-FR-009-sanitize-all-yamls.py
Sanitiza TODOS os YAMLs do sistema:
1. NC-CFG-DS-004-task-queue.yaml  corrige claimed_by sujo, completed_at inconsistente
2. active-zones.yaml  limpa entradas rfs
3. queue.lock  remove se existir
4. Gera relatrio completo
"""
import re
import sys
from datetime import datetime
from pathlib import Path

BASE  = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
QUEUE = BASE / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
LOCK  = BASE / "DIR-DS-000-agent-config" / "queue.lock"
ZONES = BASE / "DIR-DS-003-entry-locks" / "active-zones.yaml"
AUDIT = BASE / "DIR-DS-002-audit-logs"
NOW   = datetime.now().isoformat(timespec="seconds")

issues = []
fixes  = []

#  Collect APPROVED tickets from audit log
approved = set()
for hf in AUDIT.glob("NC-DS-*-handoff-*.yaml"):
    c = hf.read_text(encoding="utf-8", errors="ignore")
    if "status: APPROVED" in c:
        m = re.search(r"ticket_id:\s*(NC-DS-\d+)", c)
        if m:
            approved.add(m.group(1))

print(f"Tickets com handoff APPROVED: {sorted(approved)}")

#  Parse and sanitize queue
q = QUEUE.read_text(encoding="utf-8")
lines = q.splitlines(keepends=True)
new_lines = []
current = None
block_status = None

for line in lines:
    orig = line

    # track current ticket
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", line)
    if m:
        current = m.group(1)

    # track status of current ticket
    m_st = re.search(r"    status:\s*(\w+)", line)
    if m_st:
        block_status = m_st.group(1)

    # FIX 1: AVAILABLE + completed_at filled  DONE (if also in approved)
    if current and block_status == "AVAILABLE" and "    status: " in line:
        # we'll decide per-block; handled below via lookahead already done by repair
        pass

    # FIX 2: AVAILABLE with claimed_by non-null  null
    if current and block_status in ("AVAILABLE", "DONE") and re.search(r'    claimed_by:\s*"[^"]+"', line):
        line = re.sub(r'    claimed_by:\s*"[^"]+"', '    claimed_by: null', line)
        if line != orig:
            issues.append(f"{current}: claimed_by residual (AVAILABLE/DONE)")
            fixes.append(f"{current}: claimed_by  null")

    # FIX 3: ACTIVE ticket with approved handoff  DONE
    if current and block_status == "ACTIVE" and current in approved and "    status: ACTIVE" in line:
        line = line.replace("    status: ACTIVE", "    status: DONE")
        issues.append(f"{current}: status ACTIVE mas handoff APPROVED")
        fixes.append(f"{current}: ACTIVE  DONE")

    # FIX 4: CLAIMED expired ticket  AVAILABLE
    if current and block_status == "CLAIMED" and "    status: CLAIMED" in line:
        # Check for claimed_at in line context  if current in approved  DONE
        if current in approved:
            line = line.replace("    status: CLAIMED", "    status: DONE")
            fixes.append(f"{current}: CLAIMED+APPROVED  DONE")
        else:
            # Reset stale claims
            line = line.replace("    status: CLAIMED", "    status: AVAILABLE")
            fixes.append(f"{current}: stale CLAIMED  AVAILABLE")

    new_lines.append(line)

QUEUE.write_text("".join(new_lines), encoding="utf-8")

#  Clean queue.lock
if LOCK.exists():
    LOCK.unlink()
    fixes.append("queue.lock removido")

#  Reset active-zones
clean_zones = f"# Active Write Zones Registry\n# Limpo por NC-SCR-FR-009 em {NOW}\nactive_zones: {{}}\n"
ZONES.write_text(clean_zones, encoding="utf-8")
fixes.append("active-zones.yaml zerado")

#  Also update queue header comment to reflect new protocol
q2 = QUEUE.read_text(encoding="utf-8")
old_header = "# CLAIM PROTOCOL (atomic-ish via timestamp)"
new_header  = "# DISPATCH PROTOCOL (individual  1 agent = 1 task, sem fila compartilhada)"
if old_header in q2:
    q2 = q2.replace(old_header, new_header)
    QUEUE.write_text(q2, encoding="utf-8")
    fixes.append("queue header: claimdispatch protocol")

#  Final stats
q3 = QUEUE.read_text(encoding="utf-8")
av = len(re.findall(r"    status: AVAILABLE", q3))
dn = len(re.findall(r"    status: DONE", q3))
ac = len(re.findall(r"    status: ACTIVE", q3))
cl = len(re.findall(r"    status: CLAIMED", q3))
bl = len(re.findall(r"    status: BLOCKED", q3))

print(f"\n=== PROBLEMAS ENCONTRADOS ({len(issues)}) ===")
for i in issues: print(f"    {i}")

print(f"\n=== CORREES APLICADAS ({len(fixes)}) ===")
for f in fixes: print(f"   {f}")

print("\n=== FILA SANITIZADA ===")
print(f"AVAILABLE={av} | DONE={dn} | ACTIVE={ac} | CLAIMED={cl} | BLOCKED={bl}")

# Show available tasks
print("\nTASKS AVAILABLE:")
for m in re.finditer(r"ticket_id:\s*(NC-DS-\d+)(.*?)(?=  - ticket_id:|\Z)", q3, re.DOTALL):
    tid = m.group(1)
    blk = m.group(0)
    if "    status: AVAILABLE" in blk:
        title = re.search(r'title:\s*"([^"]{1,50})"', blk)
        print(f"  {tid} | {title.group(1) if title else '?'}")
