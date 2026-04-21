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
