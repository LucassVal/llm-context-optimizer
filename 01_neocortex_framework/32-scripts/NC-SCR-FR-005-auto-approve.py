# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.630066'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-005-auto-approve
t
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.630066'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-005-auto-approve
t
---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.630066'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-005-auto-approve
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-005-auto-approve.py
Auto-aprovao de handoffs T1  T0.

Executa: python NC-SCR-FR-005-auto-approve.py [--dry-run]

Lgica:
  1. Varre DIR-DS-002-audit-logs/ por handoffs PENDING_REVIEW
  2. Avalia critrios de auto-aprovao via NC-CFG-DS-004
  3. PASS  atualiza status para APPROVED + marca task DONE na fila
  4. FAIL  deixa PENDING_REVIEW para T0 revisar
  5. Gera log em DIR-DS-002-audit-logs/auto-approve-{timestamp}.log
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_config():
    """Obtm configurao via get_config() do NeoCortex."""
    try:
        spec = importlib.util.spec_from_file_location(
            "config",
            Path(__file__).parent.parent / "neocortex" / "core" / "config.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.get_config()
    except Exception:
        return None


def load_yaml_simple(path: Path) -> dict:
    """Parser YAML minimalista sem dependncia externa."""
    try:
        import yaml  # type: ignore

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # fallback: l linha a linha para campos simples
        data: dict = {}
        with open(path, encoding="utf-8") as f:
            for line in f:
                if ":" in line and not line.strip().startswith("#"):
                    key, _, val = line.partition(":")
                    data[key.strip()] = val.strip().strip('"')
        return data


def dump_yaml_field(path: Path, field: str, value: str) -> None:
    """Substitui um campo simples no YAML sem parser completo."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{field}:"):
            indent = len(line) - len(line.lstrip())
            new_lines.append(" " * indent + f'{field}: "{value}"\n')
        else:
            new_lines.append(line)
    path.write_text("".join(new_lines), encoding="utf-8")


def iso_now() -> str:
    """ISO 8601 completo (GOV-013)."""
    return datetime.now().isoformat(timespec="seconds")


def evaluate_handoff(handoff: dict, policy: dict) -> tuple[bool, str]:
    """
    Avalia se handoff atende critrios de auto-aprovao.

    Returns:
        (approved: bool, reason: str)
    """
    summary = handoff.get("summary", {})
    barriers = summary.get("barriers_passed", [])
    locks = summary.get("locks_violated", [])
    overall = summary.get("overall", "")
    lines = summary.get("lines_added", 0)

    # Critrio: overall == ESCALATED  T0 obrigatrio
    if overall == "ESCALATED":
        return False, "ESCALATED  requer interveno T0"

    # Critrio: locks violados
    if locks:
        return False, f"Locks violados: {locks}"

    # Critrio: barreiras obrigatrias
    required = policy.get("approve_if_all_pass", [])
    for crit in required:
        if "barriers_passed_includes" in crit:
            needed = crit["barriers_passed_includes"]
            missing = [b for b in needed if b not in barriers]
            if missing:
                return False, f"Barreiras faltando: {missing}"

        if "locks_violated_is_empty" in crit and crit["locks_violated_is_empty"]:
            if locks:
                return False, "locks_violated no vazio"

        if "overall_equals" in crit:
            if overall != crit["overall_equals"]:
                return False, f"overall={overall}  {crit['overall_equals']}"

        if "lines_added_gt" in crit:
            if lines <= crit["lines_added_gt"]:
                return False, f"lines_added={lines} suspeito (muito pouco entregue)"

    return True, "Todos os critrios de auto-aprovao atendidos"


def update_task_queue(queue_path: Path, ticket_id: str) -> None:
    """Marca task como DONE na fila NC-CFG-DS-004."""
    try:
        content = queue_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
        new_lines = []
        in_task = False
        for line in lines:
            if f"ticket_id: {ticket_id}" in line:
                in_task = True
            if in_task and "status: AVAILABLE" in line:
                line = line.replace("status: AVAILABLE", "status: DONE")
                in_task = False
            elif in_task and "status: CLAIMED" in line:
                line = line.replace("status: CLAIMED", "status: DONE")
                in_task = False
            new_lines.append(line)
        queue_path.write_text("".join(new_lines), encoding="utf-8")
        logger.info(f"Queue: {ticket_id}  DONE")
    except Exception as e:
        logger.error(f"Erro ao atualizar fila: {e}")


def run(dry_run: bool = False) -> dict:
    """Executa ciclo de auto-aprovao."""
    cfg = get_config()
    base = Path(cfg.base_dir) if cfg else Path(__file__).parent.parent.parent

    audit_dir = base / "DIR-DS-002-audit-logs"
    queue_path = base / "DIR-DS-000-agent-config" / "NC-CFG-DS-004-task-queue.yaml"
    log_path = audit_dir / f"auto-approve-{iso_now().replace(':', '-')}.log"

    queue_data = load_yaml_simple(queue_path) if queue_path.exists() else {}
    policy = queue_data.get("auto_approve", {})

    results = {"approved": [], "pending_t0": [], "skipped": [], "timestamp": iso_now()}

    handoffs = sorted(audit_dir.glob("*-handoff-*.yaml"))
    logger.info(f"Encontrados {len(handoffs)} handoffs para avaliar")

    for hpath in handoffs:
        handoff = load_yaml_simple(hpath)
        status = handoff.get("status", "")
        ticket_id = handoff.get("ticket_id", hpath.stem)

        if status != "PENDING_REVIEW":
            results["skipped"].append(ticket_id)
            continue

        approved, reason = evaluate_handoff(handoff, policy)

        if approved:
            logger.info(f"AUTO-APPROVE: {ticket_id}  {reason}")
            results["approved"].append({"ticket_id": ticket_id, "reason": reason})

            if not dry_run:
                dump_yaml_field(hpath, "status", "APPROVED")
                dump_yaml_field(hpath, "reviewed_at", iso_now())
                update_task_queue(queue_path, ticket_id)
        else:
            logger.warning(f"PENDING T0: {ticket_id}  {reason}")
            results["pending_t0"].append({"ticket_id": ticket_id, "reason": reason})

    # Relatrio
    report_lines = [
        f"# Auto-Approve Report  {iso_now()}",
        f"dry_run: {dry_run}",
        "",
        f"##  Auto-aprovados ({len(results['approved'])})",
    ]
    for r in results["approved"]:
        report_lines.append(f"- {r['ticket_id']}: {r['reason']}")
    report_lines += [
        "",
        f"##  Pendentes T0 ({len(results['pending_t0'])})",
    ]
    for r in results["pending_t0"]:
        report_lines.append(f"- {r['ticket_id']}: {r['reason']}")

    if not dry_run:
        log_path.write_text("\n".join(report_lines), encoding="utf-8")
        logger.info(f"Log salvo: {log_path}")

    print("\n".join(report_lines))
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    dry = "--dry-run" in sys.argv
    results = run(dry_run=dry)
    approved = len(results["approved"])
    pending = len(results["pending_t0"])
    print(f"\nRESUMO: {approved} auto-aprovados | {pending} pendentes T0")
