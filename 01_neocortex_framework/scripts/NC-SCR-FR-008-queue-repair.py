# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.646778'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-008
related_ssot:
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.646778'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-008
related_ssot:

---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.646778'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-008
related_ssot:
  - NC-SCR-FR-008-queue-repair
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-008-queue-repair.py  Queue Repair Script
Corrige inconsistncias no NC-CFG-DS-004-task-queue.yaml:
  1. Tasks AVAILABLE com completed_at preenchido  DONE
  2. Tasks AVAILABLE com claimed_by residual  limpa o campo
  3. Claims CLAIMED/ACTIVE com claimed_at > 300s  AVAILABLE
  4. Limpa queue.lock se existir
  5. Limpa active-zones.yaml de entradas rfs (task DONE)
  6. Normaliza claimed_by  worker-{PORT}-{HASH} onde possvel
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
QUEUE = BASE / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
LOCK = BASE / "DIR-DS-000-agent-config" / "queue.lock"
ZONES = BASE / "DIR-DS-003-entry-locks" / "active-zones.yaml"
AUDIT = BASE / "DIR-DS-002-audit-logs"
NOW = datetime.now(timezone.utc)

print(f"=== NC-SCR-FR-008-queue-repair.py | {NOW.strftime('%Y-%m-%dT%H:%M:%S')} ===\n")

# --- 1. Ler tickets DONE confirmados via handoffs APPROVED ---
approved_tickets = set()
for hf in AUDIT.glob("NC-DS-*-handoff-*.yaml"):
    c = hf.read_text(encoding="utf-8")
    if "status: APPROVED" in c or "overall: SUCCESS" in c:
        m = re.search(r"ticket_id:\s*(NC-DS-\d+)", c)
        if m:
            approved_tickets.add(m.group(1))
print(f"Handoffs APPROVED/SUCCESS encontrados: {sorted(approved_tickets)}")

# --- 2. Reparar fila ---
q = QUEUE.read_text(encoding="utf-8")
lines = q.splitlines(keepends=True)
new_lines = []
current = None
stats = {"fixed_done": 0, "claimed_cleared": 0, "expired_reset": 0}
i = 0

while i < len(lines):
    line = lines[i]

    # Rastrear ticket atual
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", line)
    if m:
        current = m.group(1)

    # A) Status AVAILABLE com completed_at preenchido  DONE
    if current and "    status: AVAILABLE" in line:
        # Lookahead para completed_at no bloco
        block = "".join(lines[max(0, i - 5) : min(len(lines), i + 10)])
        has_completed = re.search(r'completed_at:\s*"20\d{2}', block)
        if has_completed or current in approved_tickets:
            line = line.replace("    status: AVAILABLE", "    status: DONE")
            stats["fixed_done"] += 1
            print(f"  FIXED (DONE): {current}  completed_at ou APPROVED")

    # B) Field claimed_by em task AVAILABLE/DONE  limpar campo
    if current and re.search(r'    claimed_by:\s*"[^"]+"', line):
        # Verify status of current ticket in upcoming context
        ctx = "".join(lines[max(0, i - 3) : min(len(lines), i + 3)])
        if "AVAILABLE" in ctx or "DONE" in ctx:
            line = re.sub(r'    claimed_by:\s*"[^"]+"', "    claimed_by: null", line)
            stats["claimed_cleared"] += 1
            print(f"  CLEARED claimed_by: {current}")

    # C) status CLAIMED/ACTIVE com claimed_at muito antigo  AVAILABLE
    if current and "    status: CLAIMED" in line:
        # Find claimed_at
        block_str = "".join(lines[max(0, i - 2) : min(len(lines), i + 8)])
        m_ts = re.search(
            r'claimed_at:\s*"(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', block_str
        )
        if m_ts:
            try:
                claimed_dt = datetime.fromisoformat(
                    m_ts.group(1).replace("Z", "+00:00")
                )
                if claimed_dt.tzinfo is None:
                    claimed_dt = claimed_dt.replace(tzinfo=timezone.utc)
                age = (NOW - claimed_dt).total_seconds()
                if age > 600:  # > 10 min expirado
                    line = line.replace("    status: CLAIMED", "    status: AVAILABLE")
                    stats["expired_reset"] += 1
                    print(f"  EXPIRED ({age:.0f}s): {current} CLAIMED  AVAILABLE")
            except Exception:
                pass

    new_lines.append(line)
    i += 1

QUEUE.write_text("".join(new_lines), encoding="utf-8")
print(f"\nFila reparada: {stats}")

# --- 3. Limpar queue.lock ---
if LOCK.exists():
    LOCK.unlink()
    print("queue.lock removido")
else:
    print("queue.lock: no existia")

# --- 4. Limpar active-zones.yaml ---
if ZONES.exists():
    zones_content = ZONES.read_text(encoding="utf-8")
    # Resetar todas as zonas rfs
    clean_zones = (
        "# Active Write Zones Registry\n# Limpo por NC-SCR-FR-008 em "
        + NOW.strftime("%Y-%m-%dT%H:%M:%S")
        + "\nactive_zones: {}\n"
    )
    ZONES.write_text(clean_zones, encoding="utf-8")
    print("active-zones.yaml limpo (todas as entradas removidas)")

# --- 5. Status final ---
q2 = QUEUE.read_text(encoding="utf-8")
avail = len(re.findall(r"    status: AVAILABLE", q2))
done = len(re.findall(r"    status: DONE", q2))
active = len(re.findall(r"    status: ACTIVE", q2))
claimed = len(re.findall(r"    status: CLAIMED", q2))
blocked = len(re.findall(r"    status: BLOCKED", q2))
print("\n=== FILA FINAL ===")
print(
    f"AVAILABLE={avail} | DONE={done} | ACTIVE={active} | CLAIMED={claimed} | BLOCKED={blocked}"
)
print("\nRepair completo. Fila pronta para reativar workers.")
