#!/usr/bin/env python3
"""
Lista tickets ativos (com integrity_hash) que esto rfos (sem handoff).
"""

import yaml
import re
from pathlib import Path

TICKETS_DIR = Path("DIR-DS-001-tickets")
HANDOFFS_DIR = Path("DIR-DS-002-audit-logs")


def extract_ticket_id_from_filename(filename):
    match = re.match(r"(NC-DS-\d{2,3})", filename)
    return match.group(1) if match else None


def main():
    # Carregar handoffs
    handoff_ids = set()
    for hf in HANDOFFS_DIR.glob("*.yaml"):
        try:
            with open(hf, "r", encoding="utf-8") as f:
                docs = list(yaml.safe_load_all(f))
                for doc in docs:
                    if doc and "ticket_id" in doc:
                        handoff_ids.add(doc["ticket_id"])
        except Exception as e:
            print(f"Erro ao ler {hf}: {e}")

    # Processar tickets
    active_orphans = []
    for tf in TICKETS_DIR.glob("*.yaml"):
        ticket_id = extract_ticket_id_from_filename(tf.name)
        if not ticket_id:
            continue
        if ticket_id in handoff_ids:
            continue

        try:
            with open(tf, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "integrity_hash" in data:
                    # Ticket ativo (com hash)
                    title = data.get("title", data.get("ticket_type", ""))
                    active_orphans.append((ticket_id, tf.name, title))
        except Exception as e:
            print(f"Erro ao processar {tf}: {e}")

    print(f"Tickets ativos rfos: {len(active_orphans)}\n")
    for ticket_id, filename, title in active_orphans:
        print(f"{ticket_id} - {filename}")
        print(f"  Ttulo: {title}")
        print()

    # Salvar lista
    report_path = Path("DIR-DS-002-audit-logs/active_orphaned_tickets.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Tickets Ativos rfos (sem handoff)\n\n")
        f.write(f"Total: {len(active_orphans)}\n\n")
        for ticket_id, filename, title in active_orphans:
            f.write(f"## {ticket_id} - {filename}\n")
            f.write(f"**Ttulo**: {title}\n")
            f.write(f"**Arquivo**: `{filename}`\n")
            f.write("**Ao**: Verificar se rotina foi concluda e criar handoff.\n\n")

    print(f"Relatrio salvo em: {report_path}")


if __name__ == "__main__":
    main()
