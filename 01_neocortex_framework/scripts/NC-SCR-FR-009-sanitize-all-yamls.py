import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.652783'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-009-sanitize-all-yamls
related_ssot:
  - NC-SCR-FR-009
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-009-sanitize-all-yamls.py
Sanitiza TODOS os YAMLs do sistema:
1. NC-CFG-DS-004-task-queue.yaml  corrige claimed_by sujo, completed_at inconsistente
2. active-zones.yaml  limpa entradas rfs
3. queue.lock  remove se existir
4. Gera relatrio completo

Modo --check-only: apenas reporta problemas sem aplicar correções
"""
import importlib.util
import re
import sys
from datetime import datetime
from pathlib import Path

# Parse arguments
check_only = "--check-only" in sys.argv

BASE = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42")
QUEUE = BASE / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
LOCK = BASE / "DIR-DS-000-agent-config" / "queue.lock"
ZONES = BASE / "DIR-DS-003-entry-locks" / "active-zones.yaml"
AUDIT = BASE / "DIR-DS-002-audit-logs"
NOW = datetime.now().isoformat(timespec="seconds")

# Import WALService
_wal_path = (
    BASE / "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-016-wal-service.py"
)
_spec = importlib.util.spec_from_file_location("wal_service", _wal_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WALService = _mod.WALService

issues = []
fixes = []

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

    # FIX 1: AVAILABLE with approved handoff  DONE
    if (
        current
        and block_status == "AVAILABLE"
        and "    status: AVAILABLE" in line
        and current in approved
    ):
        line = line.replace("    status: AVAILABLE", "    status: DONE")
        issues.append(f"{current}: AVAILABLE mas handoff APPROVED")
        fixes.append(f"{current}: AVAILABLE  DONE (handoff aprovado)")

    # FIX 2: AVAILABLE with claimed_by non-null  null
    if (
        current
        and block_status in ("AVAILABLE", "DONE")
        and re.search(r'    claimed_by:\s*"[^"]+"', line)
    ):
        line = re.sub(r'    claimed_by:\s*"[^"]+"', "    claimed_by: null", line)
        if line != orig:
            issues.append(f"{current}: claimed_by residual (AVAILABLE/DONE)")
            fixes.append(f"{current}: claimed_by  null")

    # FIX 3: ACTIVE ticket with approved handoff  DONE
    if (
        current
        and block_status == "ACTIVE"
        and current in approved
        and "    status: ACTIVE" in line
    ):
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

if not check_only:
    wal = WALService()
    session_id = f"ciclo3-sanitize-yamls-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    with wal.transaction(session_id, "NC-SCR-FR-009", ticket_id="NC-DS-089") as txn:
        # Write queue
        before_queue = txn.before_write(QUEUE)
        QUEUE.write_text("".join(new_lines), encoding="utf-8")
        txn.after_write(QUEUE, before_queue)

        # Remove lock file
        if LOCK.exists():
            before_lock = txn.before_write(LOCK)
            LOCK.unlink()
            txn.log_delete(LOCK, before_lock)
            fixes.append("queue.lock removido")

        # Update active-zones with valid write zones
        clean_zones = f"""# Active Write Zones Registry
# Reconstruído por NC-SCR-FR-009 (NC-DS-102) em {NOW}
active_zones:
  scripts:
    - "01_neocortex_framework/scripts/"
  services:
    - "01_neocortex_framework/neocortex/core/services/"
    - "01_neocortex_framework/neocortex/core/adapters/"
    - "01_neocortex_framework/neocortex/core/hooks/"
  tools:
    - "01_neocortex_framework/neocortex/mcp/tools/"
  docs:
    - "01_neocortex_framework/DIR-DOC-FR-001-docs-main/"
  data_stores:
    - "DIR-DS-000-agent-config/"
    - "DIR-DS-001-tickets/"
    - "DIR-DS-002-audit-logs/"
    - "DIR-DS-003-wal/"
    - "DIR-DS-004-patches/"
  boot:
    - "DIR-BOOT-FR-001-bootup-main/"
  archive:
    - "DIR-ARC-FR-001-archive-main/"
  reports:
    - "reports/"
  config:
    - "01_neocortex_framework/DIR-CFG-FR-001-config-main/"
"""
        before_zones = txn.before_write(ZONES)
        ZONES.write_text(clean_zones, encoding="utf-8")
        txn.after_write(ZONES, before_zones)
        fixes.append("active-zones.yaml reconstruído com zonas válidas")

        # Update queue header
        q2 = QUEUE.read_text(encoding="utf-8")
        old_header = "# CLAIM PROTOCOL (atomic-ish via timestamp)"
        new_header = (
            "# DISPATCH PROTOCOL (individual  1 agent = 1 task, sem fila compartilhada)"
        )
        if old_header in q2:
            q2 = q2.replace(old_header, new_header)
            before_queue2 = txn.before_write(QUEUE)
            QUEUE.write_text(q2, encoding="utf-8")
            txn.after_write(QUEUE, before_queue2)
            fixes.append("queue header: claim→dispatch protocol")
else:
    print("[CHECK-ONLY] Não escrevendo alterações na fila")
    if LOCK.exists():
        fixes.append("[CHECK-ONLY] queue.lock seria removido")
    fixes.append("[CHECK-ONLY] active-zones.yaml seria reconstruído com zonas válidas")
    # Check header update
    q2 = QUEUE.read_text(encoding="utf-8")
    old_header = "# CLAIM PROTOCOL (atomic-ish via timestamp)"
    new_header = (
        "# DISPATCH PROTOCOL (individual  1 agent = 1 task, sem fila compartilhada)"
    )
    if old_header in q2:
        fixes.append(
            "[CHECK-ONLY] queue header seria atualizado: claim → dispatch protocol"
        )

#  Final stats
q3 = QUEUE.read_text(encoding="utf-8")
av = len(re.findall(r"    status: AVAILABLE", q3))
dn = len(re.findall(r"    status: DONE", q3))
ac = len(re.findall(r"    status: ACTIVE", q3))
cl = len(re.findall(r"    status: CLAIMED", q3))
bl = len(re.findall(r"    status: BLOCKED", q3))

# PASSO 5 — TAG-NORMALIZER: validar símbolos ubíquos em tickets (NC-DS-092)
_norm_path = (
    BASE
    / "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-018-tag-normalizer.py"
)
_norm_violations = 0
_norm_unknown = 0
try:
    import importlib.util as _ilu_norm

    _norm_spec = _ilu_norm.spec_from_file_location("tag_normalizer", _norm_path)
    _norm_mod = _ilu_norm.module_from_spec(_norm_spec)  # type: ignore[arg-type]
    import sys as _sys_norm

    _sys_norm.modules["tag_normalizer"] = _norm_mod  # Python 3.12+ @dataclass fix
    _norm_spec.loader.exec_module(_norm_mod)  # type: ignore[union-attr]
    TagNormalizerService = _norm_mod.TagNormalizerService
    normalizer = TagNormalizerService()
    _scan = normalizer.scan(BASE / "DIR-DS-001-tickets", recursive=False)
    _norm_violations = len(_scan.invalid)
    _norm_unknown = len(_scan.unknown)
    print(
        f"\nTAG-NORMALIZER: {_scan.scanned} arquivos | "
        f"{len(_scan.found)} símbolos válidos | "
        f"{_norm_violations} inválidos | "
        f"{_norm_unknown} desconhecidos"
    )
    if _scan.unknown:
        for u in _scan.unknown[:5]:
            print(f"  UNKNOWN: {u['symbol']} em {u['file']}:{u['line']}")
except Exception as _e_norm:
    print(f"\nTAG-NORMALIZER: ERRO ao executar — {_e_norm}")

print(f"\n=== PROBLEMAS ENCONTRADOS ({len(issues)}) ===")
for i in issues:
    print(f"    {i}")

print(f"\n=== CORREES APLICADAS ({len(fixes)}) ===")
for f in fixes:
    print(f"   {f}")

print("\n=== FILA SANITIZADA ===")
print(f"AVAILABLE={av} | DONE={dn} | ACTIVE={ac} | CLAIMED={cl} | BLOCKED={bl}")

# Show available tasks
print("\nTASKS AVAILABLE:")
for m in re.finditer(
    r"ticket_id:\s*(NC-DS-\d+)(.*?)(?=  - ticket_id:|\Z)", q3, re.DOTALL
):
    tid = m.group(1)
    blk = m.group(0)
    if "    status: AVAILABLE" in blk:
        title = re.search(r'title:\s*"([^"]{1,50})"', blk)
        print(f"  {tid} | {title.group(1) if title else '?'}")
