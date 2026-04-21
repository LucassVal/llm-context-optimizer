#!/usr/bin/env python3
"""
Auditoria de tickets YAML vs handoffs para identificar rotinas inertes.
Extrai IDs de tickets e handoffs e compara.
"""

import os
import yaml
import re
from pathlib import Path

TICKETS_DIR = Path("DIR-DS-001-tickets")
HANDOFFS_DIR = Path("DIR-DS-002-audit-logs")


def extract_ticket_id_from_filename(filename):
    """Extrai ID do ticket do nome do arquivo (ex: NC-DS-063-FIX-001.yaml -> NC-DS-063)"""
    match = re.match(r"(NC-DS-\d{2,3})", filename)
    if match:
        return match.group(1)
    return None


def extract_ticket_id_from_content(filepath):
    """Extrai ID do ticket do contedo YAML (campo 'id')"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            if content and "id" in content:
                return content["id"]
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
    return None


def extract_handoff_ticket_id(filepath):
    """Extrai ticket_id do handoff YAML"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            if content and "ticket_id" in content:
                return content["ticket_id"]
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
    return None


def main():
    print("=== AUDITORIA DE TICKETS YAML vs HANDOFFS ===\n")

    # Coletar tickets
    ticket_files = list(TICKETS_DIR.glob("*.yaml"))
    print(f"Total de tickets YAML encontrados: {len(ticket_files)}")

    ticket_ids_from_files = set()
    ticket_ids_from_content = set()
    tickets_without_id = []

    for tf in ticket_files:
        file_id = extract_ticket_id_from_filename(tf.name)
        if file_id:
            ticket_ids_from_files.add(file_id)
        content_id = extract_ticket_id_from_content(tf)
        if content_id:
            ticket_ids_from_content.add(content_id)
        else:
            tickets_without_id.append(tf.name)

    # IDs nicos (unio de ambos)
    all_ticket_ids = ticket_ids_from_files.union(ticket_ids_from_content)
    print(f"IDs de tickets nicos encontrados: {len(all_ticket_ids)}")
    if tickets_without_id:
        print(f"Tickets sem ID no contedo: {tickets_without_id}")

    # Coletar handoffs
    handoff_files = list(HANDOFFS_DIR.glob("*.yaml"))
    print(f"\nTotal de handoffs YAML encontrados: {len(handoff_files)}")

    handoff_ticket_ids = set()
    handoffs_without_ticket_id = []

    for hf in handoff_files:
        ticket_id = extract_handoff_ticket_id(hf)
        if ticket_id:
            handoff_ticket_ids.add(ticket_id)
        else:
            handoffs_without_ticket_id.append(hf.name)

    print(f"IDs de tickets referenciados em handoffs: {len(handoff_ticket_ids)}")
    if handoffs_without_ticket_id:
        print(f"Handoffs sem ticket_id: {handoffs_without_ticket_id}")

    # Comparao
    orphaned_tickets = all_ticket_ids - handoff_ticket_ids
    missing_tickets = handoff_ticket_ids - all_ticket_ids

    print("\n=== RESULTADOS ===")
    print(f"Tickets ORFOS (sem handoff correspondente): {len(orphaned_tickets)}")
    if orphaned_tickets:
        print("IDs:")
        for tid in sorted(orphaned_tickets):
            print(f"  - {tid}")

    print(f"\nHandoffs sem ticket correspondente: {len(missing_tickets)}")
    if missing_tickets:
        print("IDs:")
        for tid in sorted(missing_tickets):
            print(f"  - {tid}")

    # Estatsticas
    print("\n=== ESTATSTICAS ===")
    print(
        f"Taxa de cobertura: {len(handoff_ticket_ids)} / {len(all_ticket_ids)} = {len(handoff_ticket_ids) / max(len(all_ticket_ids), 1) * 100:.1f}%"
    )
    print(
        f"Tickets inertes (rfos): {len(orphaned_tickets)} ({len(orphaned_tickets) / max(len(all_ticket_ids), 1) * 100:.1f}%)"
    )

    # Salvar relatrio
    report_path = Path("DIR-DS-002-audit-logs/ticket_audit_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Relatrio de Auditoria: Tickets vs Handoffs\n\n")
        f.write(f"Data: {os.path.basename(__file__)}\n")
        f.write(f"Total de tickets YAML: {len(ticket_files)}\n")
        f.write(f"Total de handoffs YAML: {len(handoff_files)}\n\n")
        f.write("## Tickets rfos (sem handoff)\n\n")
        if orphaned_tickets:
            for tid in sorted(orphaned_tickets):
                f.write(f"- {tid}\n")
        else:
            f.write("Nenhum ticket rfo encontrado.\n")
        f.write("\n## Handoffs sem Ticket Correspondente\n\n")
        if missing_tickets:
            for tid in sorted(missing_tickets):
                f.write(f"- {tid}\n")
        else:
            f.write("Nenhum handoff sem ticket correspondente.\n")
        f.write("\n## Recomendaes\n\n")
        f.write(
            "1. Para cada ticket rfo, verificar se a rotina foi concluda e criar handoff.\n"
        )
        f.write(
            "2. Para handoffs sem ticket, verificar se o ticket foi excludo ou renomeado.\n"
        )
        f.write(
            "3. Implementar protocolo de abertura/verificao/fechamento para evitar rotinas inertes.\n"
        )

    print(f"\nRelatrio salvo em: {report_path}")


if __name__ == "__main__":
    main()
