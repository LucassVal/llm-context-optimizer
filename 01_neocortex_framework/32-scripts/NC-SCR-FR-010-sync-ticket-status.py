# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
# Fix encoding for Windows (UTF-8)


if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.657890'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-010
related_ssot:
  - NC-SCR-FR-010-sync-ticket-status
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-010-sync-ticket-status.py
Sincroniza status de tickets YAML com o estado da fila.
L NC-AUD-DELIVERABLES e atualiza todos status_mismatch  DONE/CLOSED.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

BASE    = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
TICKETS = BASE / "DIR-DS-001-tickets"
NOW     = datetime.now().isoformat(timespec="seconds")

# Tickets auditados como DONE na fila mas OPEN no arquivo ticket
done_in_queue = [
    "NC-DS-011", "NC-DS-012", "NC-DS-013", "NC-DS-014", "NC-DS-015",
    "NC-DS-016", "NC-DS-017", "NC-DS-019", "NC-DS-020", "NC-DS-024",
    "NC-DS-025", "NC-DS-027", "NC-DS-028",
]

updated = []
not_found = []

for tid in done_in_queue:
    matches = list(TICKETS.glob(f"{tid}-*.yaml"))
    if not matches:
        not_found.append(tid)
        continue
    tf = matches[0]
    c = tf.read_text(encoding="utf-8")

    # Update status field
    if re.search(r"^status:\s*(OPEN|AVAILABLE|ACTIVE)", c, re.MULTILINE):
        c = re.sub(r"^status:\s*(OPEN|AVAILABLE|ACTIVE).*$", "status: DONE", c, flags=re.MULTILINE)
        # Add closed_at if not present
        if "closed_at:" not in c:
            c += f'\nclosed_at: "{NOW}"\nclosed_by: "NC-SCR-FR-010 sync"\n'
        tf.write_text(c, encoding="utf-8")
        updated.append(tid)
        print(f"  UPDATED {tid}  DONE ({tf.name})")
    else:
        print(f"  SKIP {tid}  status j correto ou formato diferente")

print(f"\nUpdated: {len(updated)} tickets")
if not_found:
    print(f"Not found: {not_found}")
