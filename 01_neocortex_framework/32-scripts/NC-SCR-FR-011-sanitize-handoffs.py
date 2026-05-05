# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.665640'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-011-sanitize-hando
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.665640'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-011-sanitize-hando
---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.665640'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-011-sanitize-handoffs
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-011-sanitize-handoffs.py
Sanitiza DIR-DS-002-audit-logs:
1. Identifica handoffs reais (NC-DS-{NUM}-handoff-*.yaml)
2. Para cada ticket_id, mantm apenas o melhor handoff (maior lines + APPROVED > PENDING > REJECTED)
3. Move duplicatas e rudo para DIR-ARC-FR-001-archive-main/handoffs-archive/
4. Gera relatrio final
"""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE    = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42")
LOGS    = BASE / "DIR-DS-002-audit-logs"
ARCHIVE = BASE / "DIR-ARC-FR-001-archive-main" / "handoffs-archive"
ARCHIVE.mkdir(parents=True, exist_ok=True)
NOW     = datetime.now().strftime("%Y%m%d-%H%M%S")

STATUS_RANK = {"APPROVED": 3, "PENDING_REVIEW": 2, "REJECTED": 1, "MANUAL": 0}
LINE_FIELDS = ["lines_added", "lines_of_code", "total_lines_of_code", "lines_count", "handoff_lines"]

def get_lines(content: str) -> int:
    for f in LINE_FIELDS:
        m = re.search(rf"{f}:\s*(\d+)", content)
        if m:
            v = int(m.group(1))
            if v > 0:
                return v
    return 0

def get_status(content: str) -> str:
    m = re.search(r"^status:\s*(\w+)", content, re.MULTILINE)
    return m.group(1) if m else "UNKNOWN"

def get_ticket_id(content: str) -> str:
    m = re.search(r"ticket_id:\s*(NC-DS-\d+)", content)
    return m.group(1) if m else None

#  Scan all files
all_files   = sorted(LOGS.glob("*.yaml"))
handoffs    = {}   # tid  list of (path, status, lines, content)
noise_files = []   # non-handoff files

for f in all_files:
    name = f.name
    # Handoff files: NC-DS-{NUM}-handoff-*.yaml
    if re.match(r"NC-DS-\d+-handoff-", name):
        c   = f.read_text(encoding="utf-8", errors="ignore")
        tid = get_ticket_id(c)
        if not tid:
            tid = re.search(r"NC-DS-\d+", name).group(0) if re.search(r"NC-DS-\d+", name) else "UNKNOWN"
        st  = get_status(c)
        ln  = get_lines(c)
        handoffs.setdefault(tid, []).append((f, st, ln, c))
    else:
        # Non-handoff: NC-LOG, NC-ANL, NC-WORKER, NC-REP, NC-CRITICAL, etc.
        noise_files.append(f)

print(f"=== SCAN: {len(all_files)} arquivos totais ===")
print(f"  Handoffs: {sum(len(v) for v in handoffs.values())} ({len(handoffs)} tickets nicos)")
print(f"  Rudo (non-handoff): {len(noise_files)}")
print()

#  Per-ticket: keep best, archive rest
kept     = []
archived = []

for tid, entries in sorted(handoffs.items()):
    if len(entries) == 1:
        kept.append((tid, entries[0][0], entries[0][1], entries[0][2]))
        continue

    # Sort: APPROVED first, then by lines desc
    entries.sort(key=lambda x: (STATUS_RANK.get(x[1], 0), x[2]), reverse=True)
    best = entries[0]
    kept.append((tid, best[0], best[1], best[2]))

    for dup in entries[1:]:
        dest = ARCHIVE / dup[0].name
        shutil.move(str(dup[0]), str(dest))
        archived.append((tid, dup[0].name, dup[1], dup[2]))
        print(f"  ARCHIVED DUP {tid}: {dup[0].name} ({dup[1]}, {dup[2]}L)")

print("\n=== RESULTADO HANDOFFS ===")
for tid, path, status, lines in sorted(kept):
    flag = "" if status == "APPROVED" else ("" if status == "PENDING_REVIEW" else "")
    print(f"  {flag} {tid} | {status} | {lines}L | {path.name}")

#  Archive noise files that are truly informational only
noise_archived = []
NOISE_PATTERNS = [
    r"^NC-LOG-",
    r"^NC-ANL-",
    r"^NC-WORKER-",
    r"^NC-REP-",
    r"^NC-CRITICAL",
    r"^critical-",
    r"^NC-DS-queue-",
    r"^NC-LOG-CRITICAL",
]

print("\n=== RUDO (non-handoff) ===")
for f in noise_files:
    is_noise = any(re.match(p, f.name) for p in NOISE_PATTERNS)
    if is_noise:
        dest = ARCHIVE / f.name
        shutil.move(str(f), str(dest))
        noise_archived.append(f.name)
        print(f"  ARCHIVED NOISE: {f.name}")
    else:
        print(f"  KEPT: {f.name}")

#  Summary
print("\n=== SUMRIO FINAL ===")
print(f"  Handoffs mantidos: {len(kept)}")
print(f"  Duplicatas arquivadas: {len(archived)}")
print(f"  Arquivos de rudo arquivados: {len(noise_archived)}")
remaining = list(LOGS.glob("*.yaml"))
print(f"  Arquivos restantes em audit-logs: {len(remaining)}")

#  Write cleanup report
report = LOGS / f"NC-REP-SANITIZE-{NOW}.yaml"
lines_report = [
    f"sanitize_run: \"{NOW}\"",
    f"handoffs_kept: {len(kept)}",
    f"duplicates_archived: {len(archived)}",
    f"noise_archived: {len(noise_archived)}",
    "kept_handoffs:",
]
for tid, path, status, lines in sorted(kept):
    lines_report.append(f"  - ticket: {tid}")
    lines_report.append(f"    file: \"{path.name}\"")
    lines_report.append(f"    status: {status}")
    lines_report.append(f"    lines: {lines}")
report.write_text("\n".join(lines_report), encoding="utf-8")
print(f"\nRelatrio: {report.name}")
