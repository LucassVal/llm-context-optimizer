# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.813277'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
---"""

"""Sign tickets with integrity_hash (sha256[:16] of ticket_id|write_zone|title)."""
import hashlib
import re
import sys
from pathlib import Path

ticket_dir = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\DIR-DS-001-tickets")
updated = 0
for f in sorted(ticket_dir.glob("NC-DS-0*.yaml")):
    content = f.read_text(encoding="utf-8")
    if "integrity_hash:" in content:
        print(f"SKIP (already signed): {f.name}")
        continue
    id_m  = re.search(r"ticket_id:\s*(\S+)", content)
    wz_m  = re.search(r'write_zone:\s*"?([^"\n]+)"?', content)
    ti_m  = re.search(r'title:\s*"?([^"\n]+)"?', content)
    if not (id_m and wz_m):
        print(f"SKIP (missing fields): {f.name}")
        continue
    tid   = id_m.group(1)
    wz    = wz_m.group(1).strip('"')
    title = ti_m.group(1).strip('"') if ti_m else ""
    raw   = f"{tid}|{wz}|{title}"
    h     = hashlib.sha256(raw.encode()).hexdigest()[:16]
    content = content.rstrip() + f'\nintegrity_hash: "{h}"  # sha256[:16] of ticket_id|write_zone|title\n'
    f.write_text(content, encoding="utf-8")
    print(f"{f.name}: {h}")
    updated += 1
print(f"\nTotal: {updated} tickets assinados")
