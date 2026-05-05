# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.557602'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-ANL-FR-001-full-audit-202
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.557602'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-ANL-FR-001-full-audit-202
---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.557602'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-ANL-FR-001-full-audit-20260413
tags:
  - neocortex-other
  - level-0
  - python
---"""

import json
import sys

path = r'C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\DIR-DS-002-audit-logs\NC-ANL-FR-001-full-audit-20260413.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)
print("Total:", data["total"], "| Errors:", data["errors"])
errs = [r for r in data["details"] if r["errors"]]
for r in errs:
    print("ERR:", r["file"])
    for e in r["errors"]:
        print(" ->", e[:300])
