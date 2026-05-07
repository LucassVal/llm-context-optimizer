# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
# Fix encoding for Windows (UTF-8)


if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.641682'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-007-queue-monitor
related_ssot:
  - NC-SCR-FR-007
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-007-queue-monitor.py
Monitor CLI para a fila de tarefas NC-CFG-DS-004-task-queue.yaml.
Criado: 2026-04-12

Executa: python NC-SCR-FR-007-queue-monitor.py [--watch] [--interval 30]

Output:
   NeoCortex Queue Monitor 
  AVAILABLE:  5    CLAIMED: 2
  ACTIVE:     3    DONE:    7
  
  [NC-DS-020] AVAILABLE  | PERF-001   | HIGH
  [NC-DS-021] CLAIMED    | ARCH-001   | HIGH   worker-18:27:01
  ...
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# ============================================================================
# Configurao
# ============================================================================

QUEUE_FILE = (
    Path(__file__).parent.parent
    / "DIR-DS-000-agent-config/NC-CFG-DS-004-task-queue.yaml"
)
if not QUEUE_FILE.exists():
    # fallback para caminho relativo
    QUEUE_FILE = Path("DIR-DS-000-agent-config/NC-CFG-DS-004-task-queue.yaml")

BAR_WIDTH = 20
STATUS_COLORS = {
    "AVAILABLE": "\033[92m",  # verde
    "CLAIMED": "\033[93m",  # amarelo
    "ACTIVE": "\033[96m",  # ciano
    "DONE": "\033[90m",  # cinza
    "BLOCKED": "\033[91m",  # vermelho
}
RESET = "\033[0m"

# ============================================================================
# Lgica de leitura da fila
# ============================================================================


def load_queue() -> dict:
    """Carrega e parseia o arquivo YAML da fila."""
    try:
        content = QUEUE_FILE.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            logger.error("YAML invlido: no  um dicionrio")
            return {}
        return data
    except Exception as e:
        logger.error("Erro ao ler %s: %s", QUEUE_FILE, e)
        return {}


def extract_tasks(data: dict) -> list[dict]:
    """Extrai lista de tasks do YAML."""
    tasks = []
    # tenta tasks no root
    if "tasks" in data and isinstance(data["tasks"], list):
        tasks.extend(data["tasks"])
    # procura tambm em outras sees
    for _key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "ticket_id" in item:
                    tasks.append(item)
    return tasks


def count_status(tasks: list[dict]) -> dict[str, int]:
    """Conta tasks por status."""
    counts = {"AVAILABLE": 0, "CLAIMED": 0, "ACTIVE": 0, "DONE": 0, "BLOCKED": 0}
    for task in tasks:
        status = task.get("status", "UNKNOWN")
        if status in counts:
            counts[status] += 1
        else:
            counts[status] = 1  # categoria "UNKNOWN"
    return counts


def format_bar(count: int, total: int) -> str:
    """Retorna string de barra ASCII."""
    if total == 0:
        return " " * BAR_WIDTH
    filled = int((count / total) * BAR_WIDTH)
    bar = "" * filled + "" * (BAR_WIDTH - filled)
    return bar


def format_worker_info(claimed_by: str | None, claimed_at: str | None) -> str:
    """Formata informao do worker para display."""
    if not claimed_by or not claimed_at:
        return ""
    # extrai timestamp legvel
    try:
        dt = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M:%S")
    except Exception:
        time_str = claimed_at[:8] if len(claimed_at) >= 8 else claimed_at
    # simplifica worker ID se muito longo
    worker = claimed_by
    if len(claimed_by) > 15:
        if "-" in claimed_by:
            parts = claimed_by.split("-")
            if len(parts) >= 2:
                worker = parts[-2][:3] + "-" + parts[-1][:6]
        else:
            worker = claimed_by[:12] + "..."
    return f"  {worker} ({time_str})"


# ============================================================================
# Display
# ============================================================================


def print_header():
    """Imprime cabealho ASCII."""
    print("\n" + "" * 20 + " NeoCortex Queue Monitor " + "" * 20)


def print_summary(counts: dict[str, int], total: int):
    """Imprime resumo com barras."""
    print()
    # AVAILABLE
    avail = counts.get("AVAILABLE", 0)
    print(f"  AVAILABLE: {avail:2d}  {format_bar(avail, total)}  ", end="")
    # CLAIMED
    claimed = counts.get("CLAIMED", 0)
    print(f"CLAIMED: {claimed}")
    # ACTIVE
    active = counts.get("ACTIVE", 0)
    print(f"  ACTIVE:    {active:2d}  {format_bar(active, total)}  ", end="")
    # DONE
    done = counts.get("DONE", 0)
    print(f"DONE:    {done}")
    # BLOCKED (se houver)
    blocked = counts.get("BLOCKED", 0)
    if blocked:
        print(f"  BLOCKED:   {blocked:2d}  {format_bar(blocked, total)}")
    print("  " + "" * 60)


def print_task_list(tasks: list[dict], max_lines: int = 10):
    """Lista tasks mais relevantes."""

    # ordena por prioridade (HIGH primeiro) e depois por status
    def sort_key(task):
        priority_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        status_map = {
            "ACTIVE": 0,
            "CLAIMED": 1,
            "AVAILABLE": 2,
            "BLOCKED": 3,
            "DONE": 4,
        }
        return (
            status_map.get(task.get("status", ""), 5),
            priority_map.get(task.get("priority", "LOW"), 2),
            task.get("ticket_id", ""),
        )

    sorted_tasks = sorted(tasks, key=sort_key)
    displayed = 0
    for task in sorted_tasks:
        if displayed >= max_lines:
            break
        ticket = task.get("ticket_id", "UNKNOWN")
        status = task.get("status", "UNKNOWN")
        title = task.get("title", "")
        priority = task.get("priority", "LOW")
        # trunca ttulo se muito longo
        if len(title) > 40:
            title = title[:37] + "..."
        # cor do status
        color = STATUS_COLORS.get(status, "")
        line = f"  [{ticket}] {color}{status:10}{RESET} | {title:40} | {priority}"
        # adiciona worker info se CLAIMED/ACTIVE
        if status in ("CLAIMED", "ACTIVE"):
            worker_info = format_worker_info(
                task.get("claimed_by"), task.get("claimed_at")
            )
            line += worker_info
        print(line)
        displayed += 1
    if len(sorted_tasks) > max_lines:
        print(f"  ... e mais {len(sorted_tasks) - max_lines} tasks")


def print_footer():
    """Rodap com timestamp."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print("  " + "" * 60)
    print(f"  Atualizado: {now}")
    print("  Fila: " + str(QUEUE_FILE.relative_to(Path.cwd())))


# ============================================================================
# Loop principal
# ============================================================================


def monitor_once():
    """Executa uma iterao do monitor."""
    data = load_queue()
    tasks = extract_tasks(data)
    total = len(tasks)
    counts = count_status(tasks)

    print_header()
    print_summary(counts, total)
    print_task_list(tasks)
    print_footer()


def monitor_watch(interval: int):
    """Loop contnuo com refresh."""
    try:
        while True:
            # limpa tela (ANSI escape)
            print("\033[2J\033[H", end="")
            monitor_once()
            print(f"\n  Autorefresh em {interval}s (Ctrl+C para sair)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nMonitor interrompido pelo usurio.")
        sys.exit(0)


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="Monitor da fila NeoCortex")
    parser.add_argument(
        "--watch", action="store_true", help="Modo contnuo com autorefresh"
    )
    parser.add_argument(
        "--interval", type=int, default=30, help="Intervalo em segundos (padro 30)"
    )
    parser.add_argument("--version", action="version", version="NC-SCR-FR-007 v1.0")
    args = parser.parse_args()

    # configura logging bsico
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    if args.watch:
        monitor_watch(args.interval)
    else:
        monitor_once()


if __name__ == "__main__":
    main()
